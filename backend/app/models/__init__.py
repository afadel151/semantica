from app.models.rdf import (
    Graph,
    Subject,
    Predicate,
    RDFObject,
)

# ── Ontologies ─────────────────────────────────────────────────
from app.models.ontology import (
    Ontology,
    OntologyClass,
    OntologyProperty,
    Individual,
)

# ── SPARQL ─────────────────────────────────────────────────────
from app.models.sparql import (
    SparqlHistory,
)

# ── Reasoning ──────────────────────────────────────────────────


# ── Export explicite ───────────────────────────────────────────
__all__ = [
    # RDF
    "Graph",
    "Subject",
    "Predicate",
    "RDFObject",

    # Ontologies
    "Ontology",
    "OntologyClass",
    "OntologyProperty",
    "Individual",

    # SPARQL
    "SparqlHistory",

    # Reasoning
    
]