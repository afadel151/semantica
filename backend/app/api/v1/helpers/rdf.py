

from pathlib import Path
from typing import Optional
import urllib.parse
from rdflib.namespace import RDF, RDFS, OWL, XSD
import rdflib
from rdflib import URIRef, Literal, BNode

from sqlmodel import Session
from app.models.rdf import Graph, Subject, Predicate, Object


_WELL_KNOWN_PREFIXES: dict[str, str] = {
    str(RDF):   "rdf",
    str(RDFS):  "rdfs",
    str(OWL):   "owl",
    str(XSD):   "xsd",
    "http://xmlns.com/foaf/0.1/":          "foaf",
    "http://schema.org/":                  "schema",
    "http://www.w3.org/2004/02/skos/core#": "skos",
    "http://purl.org/dc/elements/1.1/":    "dc",
    "http://purl.org/dc/terms/":           "dcterms",
    "http://www.w3.org/ns/prov#":          "prov",
}

_FORMAT_MAP: dict[str, str] = {
    ".ttl":    "turtle",
    ".n3":     "n3",
    ".nt":     "nt",
    ".nq":     "nquads",
    ".trig":   "trig",
    ".rdf":    "xml",
    ".xml":    "xml",
    ".owl":    "xml",
    ".jsonld": "json-ld",
    ".json":   "json-ld",
    ".trix":   "trix",
    ".ttls":   "turtle",
}
_MIME_FORMAT_MAP: dict[str, str] = {
    "text/turtle":                    "turtle",
    "application/x-turtle":          "turtle",
    "text/n3":                        "n3",
    "application/n-triples":          "nt",
    "application/n-quads":            "nquads",
    "application/trig":               "trig",
    "application/rdf+xml":            "xml",
    "application/owl+xml":            "xml",
    "application/ld+json":            "json-ld",
    "application/json":               "json-ld",
}


def _detect_rdf_format(filename: str, content_type: Optional[str]) -> str:
    ext = Path(filename).suffix.lower()
    if ext in _FORMAT_MAP:
        return _FORMAT_MAP[ext]
    if content_type and content_type in _MIME_FORMAT_MAP:
        return _MIME_FORMAT_MAP[content_type]
    return "turtle" 



def _prefix_form(uri: str, ns_bindings: dict[str, str]) -> Optional[str]:
    """Return 'prefix:local' if the URI matches a known namespace, else None."""
    for ns_uri, prefix in ns_bindings.items():
        if uri.startswith(ns_uri):
            local = uri[len(ns_uri):]
            if local:
                return f"{prefix}:{local}"
    return None


def _build_ns_bindings(g: rdflib.Graph) -> dict[str, str]:
    """Merge graph-declared namespaces with well-known ones (graph wins on conflict)."""
    bindings: dict[str, str] = dict(_WELL_KNOWN_PREFIXES)
    for prefix, ns in g.namespaces():
        if prefix:
            bindings[str(ns)] = str(prefix)
    return bindings

def _parse_node(node) -> tuple[str, str, bool]:
    if isinstance(node, URIRef):
        uri_str = str(node)
        if uri_str.startswith("urn:rdf-star:"):
            encoded = uri_str[13:]  # len("urn:rdf-star:")
            decoded = urllib.parse.unquote(encoded)
            return (f"<< {decoded} >>", "statement", True)
        return (uri_str, "uri", False)
    if isinstance(node, BNode):
        return (str(node), "blank", False)
    if isinstance(node, Literal):
        return (str(node), "literal", False)
    
    # Handle RDF-star nested triples (which might expose an indexable triple structure)
    try:
        s_val, _, _ = _parse_node(node[0])
        p_val, _, _ = _parse_node(node[1])
        o_val, _, _ = _parse_node(node[2])
        return (f"<< {s_val} {p_val} {o_val} >>", "statement", True)
    except Exception:
        return (str(node), "statement", True)



def _compute_graph_details(
    rdf_graph: rdflib.Graph,
    db_graph: Graph,
    db: Session,
) -> None:

    ns_bindings = _build_ns_bindings(rdf_graph)

    #   subjecturi -> { predicate_count, rdf_type}
    subj_map: dict[str, dict] = {}
    # predicate uri -> { usage_count, domain_set, range_set}
    pred_map: dict[str, dict] = {}
    # object value ->  { kind,,, datatype, language, referenced_by, prefix_form}
    obj_map: dict[str, dict] = {}

    RDF_TYPE = str(RDF.type)

    for s, p, o in rdf_graph:
        s_str, s_kind, s_is_star = _parse_node(s)
        p_str, p_kind, p_is_star = _parse_node(p)
        o_str, o_kind, o_is_star = _parse_node(o)

        if s_str not in subj_map:
            subj_map[s_str] = {"predicate_count": 0, "rdf_type": None, "is_star": s_is_star}
        subj_map[s_str]["predicate_count"] += 1
        if p_str == RDF_TYPE and subj_map[s_str]["rdf_type"] is None:
            subj_map[s_str]["rdf_type"] = o_str

        if p_str not in pred_map:
            pred_map[p_str] = {"usage_count": 0, "domains": set(), "ranges": set()}
        pred_map[p_str]["usage_count"] += 1

        if p_str == str(RDFS.domain):
            if s_str in pred_map:
                pred_map[s_str]["domains"].add(o_str)
        if p_str == str(RDFS.range):
            if s_str in pred_map:
                pred_map[s_str]["ranges"].add(o_str)

        kind = o_kind
        obj_key = o_str  

        if obj_key not in obj_map:
            obj_map[obj_key] = {
                "kind": kind,
                "datatype": None,
                "language": None,
                "prefix_form": None,
                "referenced_by": 0,
                "is_star": o_is_star,
            }
            if kind == "uri":
                obj_map[obj_key]["prefix_form"] = _prefix_form(o_str, ns_bindings)
            elif kind == "literal" and isinstance(o, Literal):
                if o.datatype:
                    obj_map[obj_key]["datatype"] = str(o.datatype)
                if o.language:
                    obj_map[obj_key]["language"] = o.language
        obj_map[obj_key]["referenced_by"] += 1

    for p_str, info in pred_map.items():
        info["domain"] = ", ".join(sorted(info.pop("domains"))) or None
        info["range"]  = ", ".join(sorted(info.pop("ranges"))) or None

    db.bulk_insert_mappings(
        Subject,
        [
            {
                "graph_id":        db_graph.id,
                "uri":             uri,
                "prefix_form":     _prefix_form(uri, ns_bindings),
                "rdf_type":        info["rdf_type"],
                "predicate_count": info["predicate_count"],
                "is_star":         info["is_star"],
            }
            for uri, info in subj_map.items()
        ],
    )

    db.bulk_insert_mappings(
        Predicate,
        [
            {
                "graph_id":    db_graph.id,
                "uri":         uri,
                "prefix_form": _prefix_form(uri, ns_bindings),
                "usage_count": info["usage_count"],
                "domain":      info["domain"],
                "range":       info["range"],
            }
            for uri, info in pred_map.items()
        ],
    )

    db.bulk_insert_mappings(
        Object,
        [
            {
                "graph_id":      db_graph.id,
                "value":         value,
                "kind":          info["kind"],
                "prefix_form":   info["prefix_form"],
                "datatype":      info["datatype"],
                "language":      info["language"],
                "referenced_by": info["referenced_by"],
                "is_star":       info["is_star"],
            }
            for value, info in obj_map.items()
        ],
    )

    db.commit()

from rdflib import Graph, URIRef, BNode, Literal

def safe_label(g: Graph, uri) -> str:
    """Get a human readable label for a URI"""
    
    # If it's a literal just return its string value
    if isinstance(uri, Literal):
        return str(uri)
    
    # If it's a blank node
    if isinstance(uri, BNode):
        return f"_:{str(uri)}"

    # Try rdfs:label first
    from rdflib import RDFS
    label = g.value(uri, RDFS.label)
    if label:
        return str(label)

    # Fall back to the local part of the URI
    s = str(uri)
    if "#" in s:
        return s.split("#")[-1]
    return s.split("/")[-1] or s


def safe_qname(g: Graph, uri) -> str:
    """Shorten a URI to prefix:localname form"""
    
    if isinstance(uri, Literal):
        return str(uri)
    
    if isinstance(uri, BNode):
        return f"_:{str(uri)}"

    # rdflib has a built-in qname method but it throws
    # if the namespace isn't registered, so we wrap it
    try:
        return g.qname(uri)
    except Exception:
        return safe_label(g, uri)


import urllib.parse

def graph_to_cytoscape(rdf_graph: rdflib.ConjunctiveGraph) -> dict:
    nodes = {}
    edges = []

    prefix_str = ""
    for k, v in rdf_graph.namespaces():
        prefix_str += f"@prefix {k if k else ''}: <{v}> .\n"

    def process_node(node_obj) -> str:
        n_id = str(node_obj)
        if isinstance(node_obj, rdflib.Literal):
            n_id = f"lit_{hash(n_id)}"
            if n_id not in nodes:
                nodes[n_id] = {
                    "data": {
                        "id":    n_id,
                        "label": str(node_obj)[:30],
                        "type":  "literal"
                    }
                }
            return n_id

        if n_id.startswith("urn:rdf-star:"):
            if n_id not in nodes:
                encoded = n_id[len("urn:rdf-star:"):]
                decoded = urllib.parse.unquote(encoded)
                sub_g = rdflib.Graph()
                try:
                    sub_g.parse(data=f"{prefix_str}\n{decoded} .", format="turtle")
                    s_in, p_in, o_in = next(iter(sub_g))
                    
                    s_in_id = process_node(s_in)
                    o_in_id = process_node(o_in)
                    
                    nodes[n_id] = {
                        "data": {
                            "id": n_id,
                            "label": safe_qname(rdf_graph, p_in),
                            "type": "statement",
                            "tooltip": f"<< {decoded} >>"
                        }
                    }
                    edges.append({
                        "data": {
                            "id": f"e_sub_{n_id}",
                            "source": s_in_id,
                            "target": n_id,
                            "label": "",
                            "type": "star_internal"
                        }
                    })
                    edges.append({
                        "data": {
                            "id": f"e_obj_{n_id}",
                            "source": n_id,
                            "target": o_in_id,
                            "label": "",
                            "type": "star_internal"
                        }
                    })
                except Exception:
                    # Fallback if parsing fails
                    nodes[n_id] = {
                        "data": {
                            "id": n_id,
                            "label": "Statement",
                            "type": "statement"
                        }
                    }
            return n_id

        if n_id not in nodes:
            nodes[n_id] = {
                "data": {
                    "id":    n_id,
                    "label": safe_label(rdf_graph, node_obj),
                    "type":  "blank" if isinstance(node_obj, rdflib.BNode) else "uri"
                }
            }
        return n_id

    for subject, predicate, obj in rdf_graph:
        s_id = process_node(subject)
        o_id = process_node(obj)

        edges.append({
            "data": {
                "id":     f"{s_id}__{str(predicate)}__{o_id}",
                "source": s_id,
                "target": o_id,
                "label":  safe_qname(rdf_graph, predicate),
                "type":   "standard"
            }
        })

    return { "nodes": list(nodes.values()), "edges": edges }