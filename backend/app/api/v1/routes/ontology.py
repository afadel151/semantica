from fastapi import File, UploadFile, Form, Depends, HTTPException, APIRouter
from sqlmodel import select, func, Session
from pathlib import Path
from datetime import datetime
import uuid
import rdflib
from rdflib import RDF, RDFS, OWL
from rdflib.term import BNode, Literal

from app.core.db import get_session 
from app.models.ontology import Ontology, Class, Property, Individual
from app.api.v1.helpers.rdf import safe_label, safe_qname, _detect_rdf_format
from app.api.v1.helpers.ontology import _compute_ontology_details, _detect_ontology_type
router = APIRouter(prefix="/ontology", tags=["ontology"])

ONTOLOGIES_STORAGE = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "files" / "ontologies"


@router.post("/upload")
async def upload_ontology(
    name:    str        = Form(...),
    file:    UploadFile = File(...),
    session: Session    = Depends(get_session),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    rdf_format = _detect_rdf_format(file.filename, file.content_type)

    g = rdflib.Graph()
    try:
        g.parse(data=content, format=rdf_format)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse ontology: {exc}")

    onto_type = _detect_ontology_type(g)   # "owl" or "rdfs"

    ONTOLOGIES_STORAGE.mkdir(parents=True, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}_{Path(file.filename).name}"
    dest_path = ONTOLOGIES_STORAGE / unique_filename
    dest_path.write_bytes(content)

    db_onto = Ontology(
        name      = name,
        format    = onto_type,            # store "owl" or "rdfs"
        file_name = file.filename,
        file_path = str(dest_path),
        file_size = len(content),
        uploaded_at = datetime.utcnow(),
    )
    session.add(db_onto)
    session.flush()

    _compute_ontology_details(g, db_onto, session)

    return {
        "id":               str(db_onto.id),
        "name":             db_onto.name,
        "format":           db_onto.format,
        "file_name":        db_onto.file_name,
        "file_size":        db_onto.file_size,
        "classes_count":    db_onto.classes_count,
        "properties_count": db_onto.properties_count,
        "individuals_count":db_onto.individuals_count,
        "uploaded_at":      db_onto.uploaded_at,
    }


@router.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    total_ontologies  = session.exec(select(func.count()).select_from(Ontology)).one()
    total_classes     = session.exec(select(func.sum(Ontology.classes_count))).one() or 0
    total_properties  = session.exec(select(func.sum(Ontology.properties_count))).one() or 0
    total_individuals = session.exec(select(func.sum(Ontology.individuals_count))).one() or 0
    owl_count  = session.exec(select(func.count()).select_from(Ontology).where(Ontology.format == "owl")).one()
    rdfs_count = session.exec(select(func.count()).select_from(Ontology).where(Ontology.format == "rdfs")).one()

    return {
        "total_ontologies":  total_ontologies,
        "total_classes":     total_classes,
        "total_properties":  total_properties,
        "total_individuals": total_individuals,
        "owl_count":         owl_count,
        "rdfs_count":        rdfs_count,
    }


@router.get("/files")
def get_files(session: Session = Depends(get_session)):
    ontologies = session.exec(select(Ontology)).all()
    return ontologies


@router.get("/{onto_id}")
def get_file(onto_id: uuid.UUID, session: Session = Depends(get_session)):
    onto = session.get(Ontology, onto_id)
    if not onto:
        raise HTTPException(status_code=404, detail="Ontology not found.")
    return onto


@router.get("/{onto_id}/stats")
def get_file_stats(onto_id: uuid.UUID, session: Session = Depends(get_session)):
    onto = session.get(Ontology, onto_id)
    if not onto:
        raise HTTPException(status_code=404, detail="Ontology not found.")

    classes_count = session.exec(
        select(func.count()).select_from(Class).where(Class.ontology_id == onto_id)
    ).one()
    properties_count = session.exec(
        select(func.count()).select_from(Property).where(Property.ontology_id == onto_id)
    ).one()
    individuals_count = session.exec(
        select(func.count()).select_from(Individual).where(Individual.ontology_id == onto_id)
    ).one()

    return {
        "id":               str(onto.id),
        "name":             onto.name,
        "format":           onto.format,
        "file_size":        onto.file_size,
        "classes_count":    classes_count,
        "properties_count": properties_count,
        "individuals_count":individuals_count,
        "uploaded_at":      onto.uploaded_at,
    }


@router.delete("/{onto_id}")
def delete_file(onto_id: uuid.UUID, session: Session = Depends(get_session)):
    onto = session.get(Ontology, onto_id)
    if not onto:
        raise HTTPException(status_code=404, detail="Ontology not found.")

    file_path = Path(onto.file_path)
    if file_path.exists():
        file_path.unlink()

    session.delete(onto)
    session.commit()
    return {"detail": f"Ontology '{onto.name}' deleted successfully."}


# ─────────────────────────────────────────
# OWL DETAIL  →  used by /owl/[id].vue
# ─────────────────────────────────────────
@router.get("/{onto_id}/owl")
def get_owl_detail(onto_id: uuid.UUID, session: Session = Depends(get_session)):
    onto = session.get(Ontology, onto_id)
    if not onto:
        raise HTTPException(status_code=404, detail="Ontology not found.")
    if onto.format != "owl":
        raise HTTPException(status_code=400, detail="This ontology is not OWL.")

    g = rdflib.Graph()
    g.parse(onto.file_path)

    classes_db = session.exec(
        select(Class).where(Class.ontology_id == onto_id)
    ).all()

    obj_props = session.exec(
        select(Property)
        .where(Property.ontology_id == onto_id)
        .where(Property.type == "owl:ObjectProperty")
    ).all()

    data_props = session.exec(
        select(Property)
        .where(Property.ontology_id == onto_id)
        .where(Property.type == "owl:DatatypeProperty")
    ).all()

    individuals = session.exec(
        select(Individual).where(Individual.ontology_id == onto_id)
    ).all()

    nodes = []
    edges = []

    # Add owl:Thing as root node (virtual — not stored in DB)
    root_uri = str(OWL.Thing)
    nodes.append({
        "id": "owl:Thing",
        "label": "owl:Thing",
        "type": "root",
        "comment": None,
        "equivalent_classes": [],
        "disjoint_classes": [],
        "union_of": [],
        "intersection_of": [],
        "object_properties": [],
        "data_properties": [],
        "restrictions": [],
        "individuals": [],
        "individual_count": 0,
    })

    class_ids = set()  # track emitted node IDs to avoid duplicates

    for cls_db in classes_db:
        cls_uri = rdflib.URIRef(cls_db.uri)
        node_id = cls_db.prefix_form or safe_qname(g, cls_uri)
        class_ids.add(node_id)

        # OWL-specific relations
        equivalents = [
            safe_qname(g, e) for e in g.objects(cls_uri, OWL.equivalentClass)
            if not isinstance(e, BNode)
        ]
        disjoints = [
            safe_qname(g, d) for d in g.objects(cls_uri, OWL.disjointWith)
            if not isinstance(d, BNode)
        ]

        union_node = g.value(cls_uri, OWL.unionOf)
        union_of = [safe_qname(g, i) for i in g.items(union_node) if not isinstance(i, BNode)] if union_node else []

        inter_node = g.value(cls_uri, OWL.intersectionOf)
        intersection_of = [safe_qname(g, i) for i in g.items(inter_node) if not isinstance(i, BNode)] if inter_node else []

        # Restrictions
        restrictions = []
        for superclass in g.objects(cls_uri, RDFS.subClassOf):
            if (superclass, RDF.type, OWL.Restriction) in g:
                prop = g.value(superclass, OWL.onProperty)
                restrictions.append({
                    "property": safe_qname(g, prop) if prop else None,
                    "min_cardinality": int(v) if (v := g.value(superclass, OWL.minCardinality)) else None,
                    "max_cardinality": int(v) if (v := g.value(superclass, OWL.maxCardinality)) else None,
                    "exact_cardinality": int(v) if (v := g.value(superclass, OWL.cardinality)) else None,
                    "some_values_from": safe_qname(g, sv) if (sv := g.value(superclass, OWL.someValuesFrom)) and not isinstance(sv, BNode) else None,
                    "all_values_from": safe_qname(g, av) if (av := g.value(superclass, OWL.allValuesFrom)) and not isinstance(av, BNode) else None,
                })

        cls_obj_props = [
            {"label": p.label, "range": p.range}
            for p in obj_props if p.domain == cls_db.prefix_form
        ]
        cls_data_props = [
            {"label": p.label, "range": p.range}
            for p in data_props if p.domain == cls_db.prefix_form
        ]
        cls_individuals = [
            {"uri": i.uri, "label": i.label}
            for i in individuals if i.rdf_type == cls_db.prefix_form
        ]
        comment = g.value(cls_uri, RDFS.comment)

        nodes.append({
            "id": node_id,
            "label": cls_db.label or node_id,
            "type": "class",
            "comment": str(comment) if comment else None,
            "equivalent_classes": equivalents,
            "disjoint_classes": disjoints,
            "union_of": union_of,
            "intersection_of": intersection_of,
            "object_properties": cls_obj_props,
            "data_properties": cls_data_props,
            "restrictions": restrictions,
            "individuals": cls_individuals,
            "individual_count": len(cls_individuals),
        })

        # ── Edges ────────────────────────────────────────────────────────────
        # subClassOf edges (excluding restriction BNodes)
        parents = [
            p for p in g.objects(cls_uri, RDFS.subClassOf)
            if not isinstance(p, BNode)
        ]
        if parents:
            for parent in parents:
                parent_id = safe_qname(g, parent)
                edges.append({
                    "source": node_id,
                    "target": parent_id,
                    "type": "subClassOf",
                })
        else:
            # No explicit parent → connect to owl:Thing
            edges.append({
                "source": node_id,
                "target": "owl:Thing",
                "type": "subClassOf",
            })

        # equivalentClass edges (undirected, emit once per pair)
        for eq in equivalents:
            edges.append({"source": node_id, "target": eq, "type": "equivalentClass"})

        # disjointWith edges
        for dj in disjoints:
            edges.append({"source": node_id, "target": dj, "type": "disjointWith"})

    return {
        "id": str(onto.id),
        "name": onto.name,
        "format": onto.format,
        "class_count": onto.classes_count,
        "object_property_count": len(obj_props),
        "data_property_count": len(data_props),
        "individual_count": onto.individuals_count,
        "nodes": nodes,
        "edges": edges,
    }

# ─────────────────────────────────────────
# RDFS DETAIL  →  used by /rdfs/[id].vue
# ─────────────────────────────────────────

@router.get("/{onto_id}/rdfs")
def get_rdfs_detail(onto_id: uuid.UUID, session: Session = Depends(get_session)):
    onto = session.get(Ontology, onto_id)
    if not onto:
        raise HTTPException(status_code=404, detail="Ontology not found.")
    if onto.format != "rdfs":
        raise HTTPException(status_code=400, detail="This ontology is not RDFS.")

    g = rdflib.Graph()
    g.parse(onto.file_path)

    classes_db    = session.exec(select(Class).where(Class.ontology_id == onto_id)).all()
    properties_db = session.exec(select(Property).where(Property.ontology_id == onto_id)).all()

    # Count namespaces from live file
    namespaces = [
        {"prefix": str(p), "uri": str(u)}
        for p, u in g.namespaces()
    ]

    classes_out = []
    for cls_db in classes_db:
        cls_uri = rdflib.URIRef(cls_db.uri)

        # Properties whose domain = this class
        cls_props = [
            {"label": p.label, "range": p.range}
            for p in properties_db
            if p.domain == cls_db.prefix_form or p.domain == cls_db.uri
        ]

        comment = g.value(cls_uri, RDFS.comment)

        classes_out.append({
            "uri":         cls_db.uri,
            "label":       cls_db.label,
            "prefix_form": cls_db.prefix_form,
            "comment":     str(comment) if comment else None,
            "parents":     [cls_db.parent_uri] if cls_db.parent_uri else [],
            "children":    [
                safe_qname(g, c) for c in g.subjects(RDFS.subClassOf, cls_uri)
                if not isinstance(c, BNode)
            ],
            "properties":  cls_props,
        })

    return {
        "id":               str(onto.id),
        "name":             onto.name,
        "format":           onto.format,
        "class_count":      onto.classes_count,
        "property_count":   onto.properties_count,
        "namespace_count":  len(namespaces),
        "namespaces":       namespaces,
        "classes":          classes_out,
    }
