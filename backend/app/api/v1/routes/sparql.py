from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session
from typing import List
import uuid
from fastapi.responses import FileResponse
import csv
import json
import tempfile
import xml.etree.ElementTree as ET
from pydantic import BaseModel
from rdflib import Graph as RDFGraph

from app.core.db import get_session
from app.models.sparql import SparqlHistory, SparqlQueryRequest, ConstructExportRequest, SparqlUpdateRequest, GenerateUpdateRequest
from app.models.rdf import Graph

router = APIRouter(prefix="/sparql", tags=["sparql"])


# Statistiques SPARQL globales
@router.get("/stats")
def get_sparql_stats(session: Session = Depends(get_session)):
    """Retourne les statistiques globales SPARQL: total, types, dernière requête."""
    all_queries = session.exec(select(SparqlHistory)).all()
    total = len(all_queries)

    type_counts: dict[str, int] = {}
    for q in all_queries:
        type_counts[q.query_type] = type_counts.get(q.query_type, 0) + 1

    # Dernière requête exécutée
    last_query = session.exec(
        select(SparqlHistory).order_by(SparqlHistory.executed_at.desc()).limit(1)
    ).first()

    last_info = None
    if last_query:
        last_info = {
            "query_type":    last_query.query_type,
            "executed_at":   last_query.executed_at.isoformat(),
            "query_snippet": last_query.query[:80] + ("..." if len(last_query.query) > 80 else ""),
        }

    return {
        "total_queries": total,
        "by_type":       type_counts,
        "last_query":    last_info,
    }


# récupérer les requêtes récentes
@router.get("/recent", response_model=List[SparqlHistory])
def get_recent_queries(session: Session = Depends(get_session)):

    queries = session.exec(
        select(SparqlHistory)
        .order_by(SparqlHistory.executed_at.desc())
        .limit(10)
    ).all()

    return queries


import urllib.parse
import re
from rdflib import URIRef, RDF as _RDF


def preprocess_sparql_star(query: str) -> str:
    """Convert << ?s ?p ?o >> patterns to standard RDF reification blank-node syntax."""
    def split_triple(inner: str):
        parts = []
        current = ""
        in_uri = False
        in_quote = False
        in_bnode = 0
        for char in inner:
            if char == '<' and not in_quote:
                in_uri = True
            elif char == '>' and not in_quote:
                in_uri = False
            elif char == '"':
                in_quote = not in_quote
            elif char == '[' and not in_quote and not in_uri:
                in_bnode += 1
            elif char == ']' and not in_quote and not in_uri:
                in_bnode -= 1
            elif char.isspace() and not in_uri and not in_quote and in_bnode == 0:
                if current:
                    parts.append(current)
                    current = ""
                continue
            current += char
        if current:
            parts.append(current)
        return parts

    def replacer(match):
        inner = match.group(1).strip()
        parts = split_triple(inner)
        if len(parts) >= 3:
            s = parts[0]
            p = parts[1]
            o = " ".join(parts[2:])
            return (
                f"[ <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> {s} "
                f"; <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> {p} "
                f"; <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> {o} ]"
            )
        return match.group(0)

    prev = ""
    while "<<" in query and ">>" in query and query != prev:
        prev = query
        query = re.sub(r'<<\s*((?:(?!<<|>>).)*?)\s*>>', replacer, query, flags=re.DOTALL)
    return query


def _add_reification_in_memory(g: RDFGraph) -> None:
    """For every urn:rdf-star: URI in the graph, inject rdf:subject/predicate/object triples."""
    prefix_str = ""
    for k, v in g.namespaces():
        prefix_str += f"@prefix {k if k else ''}: <{v}> .\n"

    star_nodes: set = set()
    for s, _p, o in g:
        if isinstance(s, URIRef) and str(s).startswith("urn:rdf-star:"):
            star_nodes.add(s)
        if isinstance(o, URIRef) and str(o).startswith("urn:rdf-star:"):
            star_nodes.add(o)

    for node in star_nodes:
        if (node, _RDF.subject, None) in g:
            continue  # already reified
        encoded = str(node)[len("urn:rdf-star:"):]
        decoded = urllib.parse.unquote(encoded)
        sub_g = RDFGraph()
        try:
            sub_g.parse(data=f"{prefix_str}\n{decoded} .", format="turtle")
            s_in, p_in, o_in = next(iter(sub_g))
            g.add((node, _RDF.type, _RDF.Statement))
            g.add((node, _RDF.subject, s_in))
            g.add((node, _RDF.predicate, p_in))
            g.add((node, _RDF.object, o_in))
        except Exception:
            pass


# Universal SPARQL executor
def execute_sparql(query: str, graph_path: str) -> dict:
    """
    Handles SELECT, ASK, DESCRIBE, CONSTRUCT + SPARQL-star + FILTER/BIND/OPTIONAL etc.
    Returns: { type, boolean, headers, rows, graph_ttl }
    """
    g = RDFGraph()
    g.parse(graph_path)

    # SPARQL-star: inject reification in-memory, then rewrite query
    if "<<" in query and ">>" in query:
        _add_reification_in_memory(g)
        query = preprocess_sparql_star(query)

    # Detect query type: strip comments / PREFIX / BASE, then find the first keyword
    def _detect_type(q: str) -> str:
        # Remove comments
        cleaned = re.sub(r'#[^\n]*', '', q)
        # Remove PREFIX and BASE declarations (can be multiline)
        cleaned = re.sub(r'(?i)\b(PREFIX|BASE)\s+\S+\s*<[^>]*>', '', cleaned)
        cleaned = cleaned.strip()
        # Match the first SPARQL keyword
        m = re.match(r'(?i)\s*(ASK|DESCRIBE|CONSTRUCT|SELECT)\b', cleaned)
        if m:
            return m.group(1).upper()
        return "SELECT"

    q_type = _detect_type(query)

    try:
        results = g.query(query)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"SPARQL error: {exc}")

    def decode_val(v) -> str:
        if v is None:
            return ""
        val = str(v)
        if val.startswith("urn:rdf-star:"):
            return f"<< {urllib.parse.unquote(val[len('urn:rdf-star:'):])} >>"
        return val

    try:
        if q_type == "ASK":
            return {"type": "ASK", "boolean": bool(results), "headers": [], "rows": [], "graph_ttl": None}

        if q_type in ("DESCRIBE", "CONSTRUCT"):
            result_graph = RDFGraph()
            for ns_p, ns_u in g.namespaces():
                result_graph.bind(ns_p, ns_u)
            triples = []
            for triple in results:
                if isinstance(triple, tuple) and len(triple) == 3:
                    s, p, o = triple
                    result_graph.add((s, p, o))
                    triples.append([decode_val(s), decode_val(p), decode_val(o)])
            ttl = result_graph.serialize(format="turtle")
            return {"type": q_type, "boolean": None, "headers": ["subject", "predicate", "object"], "rows": triples, "graph_ttl": ttl}

        # SELECT (FILTER, BIND, OPTIONAL, GROUP BY, HAVING, etc. are natively handled by RDFLib)
        vars_list = getattr(results, "vars", None) or []
        headers = [str(v) for v in vars_list]
        rows = [[decode_val(v) for v in row] for row in results]
        return {"type": "SELECT", "boolean": None, "headers": headers, "rows": rows, "graph_ttl": None}

    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"SPARQL error: {exc}")


# ─── Universal query endpoint ───────────────────────────────────────────────

# SELECT (kept for backward compat - delegates to universal executor)
@router.post("/select")
def run_select(
    data: SparqlQueryRequest,
    session: Session = Depends(get_session)
):

    graph = session.get(Graph, data.graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    try:
        result = execute_sparql(data.query, graph.file_path)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"SPARQL error: {exc}")

    history = SparqlHistory(
        query=data.query,
        query_type=result["type"],
        graph_id=data.graph_id
    )
    session.add(history)
    session.commit()

    return result




# ASK
@router.post("/ask")
def run_ask(
    data: SparqlQueryRequest,
    session: Session = Depends(get_session)
):

    graph = session.get(Graph, data.graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    # charger le graphe RDF
    g = RDFGraph()
    g.parse(graph.file_path)

    try:
        result = g.query(data.query)

        # ASK retourne un booléen
        boolean_result = bool(result)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    history = SparqlHistory(
        query=data.query,
        query_type="ASK",
        graph_id=data.graph_id
    )

    session.add(history)
    session.commit()

    return {
        "result": boolean_result
    }

# DESCRIBE
@router.post("/describe")
def run_describe(
    data: SparqlQueryRequest,
    session: Session = Depends(get_session)
):

    graph = session.get(Graph, data.graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    result = execute_sparql(data.query, graph.file_path)

    history = SparqlHistory(
        query=data.query,
        query_type="DESCRIBE",
        graph_id=data.graph_id
    )

    session.add(history)
    session.commit()

    return {"result": result}


# CONSTRUCT
@router.post("/construct")
def run_construct(
    data: SparqlQueryRequest,
    session: Session = Depends(get_session)
):

    graph = session.get(Graph, data.graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    result = execute_sparql(data.query, graph.file_path)

    history = SparqlHistory(
        query=data.query,
        query_type="CONSTRUCT",
        graph_id=data.graph_id
    )

    session.add(history)
    session.commit()

    return {"result": result}


# export (placeholder)
## Query ; ?format=(json||csv)&graph_id=graph_id&query=SELECT%20?s%20?p%20?o%20WHERE%20{%20?s%20?p%20?o%20}%20LIMIT%2010
@router.get("/export")
def export_result(
    query: str,
    graph_id: uuid.UUID,
    format: str = Query("json", enum=["json", "csv", "xml"]),
    session: Session = Depends(get_session)
):

    graph = session.get(Graph, graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    # charger le fichier RDF
    g = RDFGraph()
    g.parse(graph.file_path)

    try:
        results = g.query(query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # récupérer les variables SELECT
    headers = [str(v) for v in results.vars]

    rows = []
    for row in results:
        rows.append([str(v) if v else "" for v in row])

    if format == "json":
        data = []
        for row in rows:
            data.append(dict(zip(headers, row)))
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        with open(temp_file.name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return FileResponse(
            path=temp_file.name,
            filename="sparql_result.json",
            media_type="application/json"
        )

    if format == "csv":
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        with open(temp_file.name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return FileResponse(
            path=temp_file.name,
            filename="sparql_result.csv",
            media_type="text/csv"
        )

    if format == "xml":
        root = ET.Element("sparql", xmlns="http://www.w3.org/2005/sparql-results#")
        head = ET.SubElement(root, "head")
        for var in headers:
            ET.SubElement(head, "variable", name=var)
        results_el = ET.SubElement(root, "results")
        for row in rows:
            binding_el = ET.SubElement(results_el, "result")
            for var, val in zip(headers, row):
                b = ET.SubElement(binding_el, "binding", name=var)
                if val.startswith("http") or val.startswith("urn:"):
                    uri_el = ET.SubElement(b, "uri")
                    uri_el.text = val
                elif val.startswith("_:"):
                    bnode_el = ET.SubElement(b, "bnode")
                    bnode_el.text = val[2:]
                else:
                    lit_el = ET.SubElement(b, "literal")
                    lit_el.text = val
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        with open(temp_file.name, "wb") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)
        return FileResponse(
            path=temp_file.name,
            filename="sparql_result.xml",
            media_type="application/sparql-results+xml"
        )


@router.post("/export/construct")
def export_construct(
    data: ConstructExportRequest,
    format: str = Query("json", enum=["json", "csv", "xml"])
):
    triples = data.triples

    if format == "json":
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        with open(temp_file.name, "w", encoding="utf-8") as f:
            json.dump(
                [{"subject": t[0], "predicate": t[1], "object": t[2]} for t in triples],
                f, indent=4
            )
        return FileResponse(
            path=temp_file.name,
            filename="construct_result.json",
            media_type="application/json"
        )

    if format == "csv":
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        with open(temp_file.name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["subject", "predicate", "object"])
            writer.writerows(triples)
        return FileResponse(
            path=temp_file.name,
            filename="construct_result.csv",
            media_type="text/csv"
        )

    if format == "xml":
        from rdflib import Graph as RDFGraph, URIRef, Literal, BNode
        g = RDFGraph()
        for t in triples:
            s_val = t[0]; p_val = t[1]; o_val = t[2]
            s = BNode(s_val[2:]) if s_val.startswith("_:") else URIRef(s_val)
            p = URIRef(p_val)
            if o_val.startswith("http") or o_val.startswith("urn:") or o_val.startswith("_:"):
                o = BNode(o_val[2:]) if o_val.startswith("_:") else URIRef(o_val)
            else:
                o = Literal(o_val)
            g.add((s, p, o))
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        g.serialize(destination=temp_file.name, format="xml")
        return FileResponse(
            path=temp_file.name,
            filename="construct_result.xml",
            media_type="application/rdf+xml"
        )

# supprimer requête
@router.delete("/{query_id}")
def delete_query(
    query_id: uuid.UUID,
    session: Session = Depends(get_session)
):

    query = session.get(SparqlHistory, query_id)

    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    session.delete(query)
    session.commit()

    return {"message": "Query deleted"}


# UPDATE (INSERT / DELETE)
@router.post("/update")
def run_update(
    data: SparqlUpdateRequest,
    session: Session = Depends(get_session)
):
    """Exécute une requête SPARQL UPDATE (INSERT DATA / DELETE DATA / DELETE WHERE)."""
    import time

    graph = session.get(Graph, data.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    g = RDFGraph()
    try:
        g.parse(graph.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de charger le graphe : {e}")

    triples_before = len(g)
    start = time.time()

    try:
        g.update(data.query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur SPARQL UPDATE : {e}")

    execution_time = round((time.time() - start) * 1000)
    triples_after = len(g)
    triples_added = max(0, triples_after - triples_before)
    triples_removed = max(0, triples_before - triples_after)

    # Sauvegarder le graphe modifié sur le disque
    try:
        g.serialize(destination=graph.file_path, format=graph.format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de sauvegarder le graphe : {e}")

    # Mettre à jour le compteur de triplets en base
    graph.triples_count = triples_after
    session.add(graph)

    # Historique
    query_text = data.query.strip()
    if "INSERT" in query_text.upper():
        q_type = "INSERT"
    elif "DELETE" in query_text.upper():
        q_type = "DELETE"
    else:
        q_type = "UPDATE"

    history = SparqlHistory(
        query=data.query,
        query_type=q_type,
        graph_id=data.graph_id
    )
    session.add(history)
    session.commit()

    return {
        "success": True,
        "execution_time": execution_time,
        "triples_before": triples_before,
        "triples_after": triples_after,
        "triples_added": triples_added,
        "triples_removed": triples_removed,
        "graph_size": triples_after,
    }


# SCHEMA — pour l'autocomplétion
@router.get("/schema")
def get_schema(
    graph_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Retourne les préfixes, classes et propriétés du graphe RDF actif."""
    from rdflib.namespace import RDF, RDFS, OWL

    graph = session.get(Graph, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    g = RDFGraph()
    try:
        g.parse(graph.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de charger le graphe : {e}")

    # Préfixes déclarés
    prefixes = {}
    for prefix, namespace in g.namespaces():
        prefixes[str(prefix)] = str(namespace)

    # Classes (objets de rdf:type)
    classes = set()
    for _, _, o in g.triples((None, RDF.type, None)):
        classes.add(str(o))

    # Propriétés (prédicats utilisés)
    properties = set()
    for _, p, _ in g.triples((None, None, None)):
        properties.add(str(p))

    # Sujets (pour les suggestions d'entités)
    subjects = set()
    for s, _, _ in g.triples((None, None, None)):
        subjects.add(str(s))

    return {
        "prefixes": prefixes,
        "classes": sorted(list(classes))[:200],
        "properties": sorted(list(properties))[:200],
        "subjects": sorted(list(subjects))[:100],
        "graph_size": len(g),
    }


# GENERATE UPDATE — génération automatique de requêtes
@router.post("/generate-update")
def generate_update_query(
    data: GenerateUpdateRequest,
    session: Session = Depends(get_session)
):
    """Génère automatiquement une requête SPARQL UPDATE à partir de la structure du graphe."""
    from rdflib.namespace import RDF

    graph = session.get(Graph, data.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    g = RDFGraph()
    try:
        g.parse(graph.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de charger le graphe : {e}")

    # Récupérer les préfixes du graphe
    prefix_lines = []
    prefix_map = {}
    for prefix, namespace in g.namespaces():
        if str(prefix):  # ignorer le préfixe vide
            prefix_lines.append(f"PREFIX {prefix}: <{namespace}>")
            prefix_map[str(namespace)] = str(prefix)

    def uri_to_prefixed(uri):
        for ns, pref in prefix_map.items():
            if uri.startswith(ns):
                return f"{pref}:{uri[len(ns):]}"
        return f"<{uri}>"

    prefixes_str = "\n".join(prefix_lines[:10])  # Limiter à 10 préfixes

    if data.mode == "insert":
        # Prendre le premier triplet comme exemple
        example_triple = next(iter(g), None)
        if example_triple:
            s, p, o = example_triple
            s_str = uri_to_prefixed(str(s))
            p_str = uri_to_prefixed(str(p))
            # Objet : literal ou URI
            if hasattr(o, 'toPython'):
                o_str = f'"{str(o)}"'
            elif str(o).startswith("http") or str(o).startswith("urn:"):
                o_str = uri_to_prefixed(str(o))
            else:
                o_str = f'"{str(o)}"'
        else:
            s_str = "<http://example.org/subject>"
            p_str = "<http://example.org/predicate>"
            o_str = '"valeur"'

        query = f"""{prefixes_str}

INSERT DATA {{
  {s_str} {p_str} {o_str} .
}}"""

    elif data.mode == "delete":
        # Prendre le premier triplet comme exemple
        example_triple = next(iter(g), None)
        if example_triple:
            s, p, o = example_triple
            s_str = uri_to_prefixed(str(s))
            p_str = uri_to_prefixed(str(p))
            if hasattr(o, 'toPython'):
                o_str = f'"{str(o)}"'
            elif str(o).startswith("http") or str(o).startswith("urn:"):
                o_str = uri_to_prefixed(str(o))
            else:
                o_str = f'"{str(o)}"'
        else:
            s_str = "<http://example.org/subject>"
            p_str = "<http://example.org/predicate>"
            o_str = '"valeur"'

        query = f"""{prefixes_str}

DELETE DATA {{
  {s_str} {p_str} {o_str} .
}}"""

    else:
        # Mode générique DELETE WHERE
        query = f"""{prefixes_str}

DELETE WHERE {{
  ?subject ?predicate ?object .
}}"""

    return {
        "query": query,
        "mode": data.mode,
        "graph_size": len(g),
    }

