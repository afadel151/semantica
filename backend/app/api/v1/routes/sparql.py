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


# récupérer les requêtes récentes
@router.get("/recent", response_model=List[SparqlHistory])
def get_recent_queries(session: Session = Depends(get_session)):

    queries = session.exec(
        select(SparqlHistory)
        .order_by(SparqlHistory.executed_at.desc())
        .limit(10)
    ).all()

    return queries


# fonction interne pour exécuter SPARQL
def execute_sparql(query: str, graph_path: str):

    g = RDFGraph()
    g.parse(graph_path)

    results = g.query(query)

    data = []

    for row in results:
        data.append([str(x) for x in row])

    return data


# SELECT
@router.post("/select")
def run_select(
    data: SparqlQueryRequest,
    session: Session = Depends(get_session)
):

    graph = session.get(Graph, data.graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    result = execute_sparql(data.query, graph.file_path)

    history = SparqlHistory(
        query=data.query,
        query_type="SELECT",
        graph_id=data.graph_id
    )

    session.add(history)
    session.commit()

    return {"result": result}


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

