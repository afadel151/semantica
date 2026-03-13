from fastapi import File, HTTPException, UploadFile, Form, Depends, APIRouter
from app.models.rdf import Graph, Subject, Predicate, Object
from app.core.db import get_session
from app.api.v1.helpers.rdf import _detect_rdf_format, _compute_graph_details, graph_to_cytoscape
from sqlmodel import Session, select, func
from pathlib import Path
from datetime import datetime
import uuid
import rdflib

router = APIRouter(prefix="/rdf", tags=["rdf"])

GRAPHS_STORAGE = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "files" / "graphs"



@router.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    total_graphs    = session.exec(select(func.count()).select_from(Graph)).one()
    total_triples   = session.exec(select(func.sum(Graph.triples_count))).one() or 0
    total_subjects  = session.exec(select(func.count()).select_from(Subject)).one()
    total_predicates= session.exec(select(func.count()).select_from(Predicate)).one()
    total_objects   = session.exec(select(func.count()).select_from(Object)).one()
    return {
        "total_graphs":     total_graphs,
        "total_triples":    total_triples,
        "total_subjects":   total_subjects,
        "total_predicates": total_predicates,
        "total_objects":    total_objects,
    }



@router.get("/files")
def get_files(session: Session = Depends(get_session)):
    graphs = session.exec(select(Graph)).all()
    return graphs



@router.get("/{file_id}")
def get_file(file_id: uuid.UUID, session: Session = Depends(get_session)):
    graph = session.get(Graph, file_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")
    return graph



@router.get("/{file_id}/stats")
def get_file_stats(file_id: uuid.UUID, session: Session = Depends(get_session)):
    graph = session.get(Graph, file_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    subjects_count  = session.exec(
        select(func.count()).select_from(Subject).where(Subject.graph_id == file_id)
    ).one()
    predicates_count = session.exec(
        select(func.count()).select_from(Predicate).where(Predicate.graph_id == file_id)
    ).one()
    objects_count   = session.exec(
        select(func.count()).select_from(Object).where(Object.graph_id == file_id)
    ).one()

    return {
        "graph_id":        str(graph.id),
        "name":            graph.name,
        "format":          graph.format,
        "file_size":       graph.file_size,
        "triples_count":   graph.triples_count,
        "uploaded_at":     graph.uploaded_at,
        "subjects_count":  subjects_count,
        "predicates_count":predicates_count,
        "objects_count":   objects_count,
    }



@router.delete("/{file_id}")
def delete_file(file_id: uuid.UUID, session: Session = Depends(get_session)):
    graph = session.get(Graph, file_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    file_path = Path(graph.file_path)
    if file_path.exists():
        file_path.unlink()

    session.delete(graph)
    session.commit()
    return {"detail": f"Graph '{graph.name}' deleted successfully."}



@router.post("/upload")
async def upload_graph(
    name: str         = Form(...),
    file: UploadFile  = File(...),
    session: Session  = Depends(get_session),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    rdf_format = _detect_rdf_format(file.filename, file.content_type)

    rdf_graph = rdflib.ConjunctiveGraph()
    try:
        rdf_graph.parse(data=content, format=rdf_format)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse RDF file: {exc}")

    triples_count = len(rdf_graph)

    GRAPHS_STORAGE.mkdir(parents=True, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}_{Path(file.filename).name}"
    dest_path = GRAPHS_STORAGE / unique_filename
    dest_path.write_bytes(content)

    db_graph = Graph(
        name=name,
        format=rdf_format,
        file_name=file.filename,
        file_path=str(dest_path),
        file_size=len(content),
        triples_count=triples_count,
        uploaded_at=datetime.utcnow(),
    )
    session.add(db_graph)
    session.flush()  # get db_graph.id without closing transaction

    _compute_graph_details(rdf_graph, db_graph, session)  # commits inside

    return {
        "id":            str(db_graph.id),
        "name":          db_graph.name,
        "format":        db_graph.format,
        "file_name":     db_graph.file_name,
        "file_size":     db_graph.file_size,
        "triples_count": db_graph.triples_count,
        "uploaded_at":   db_graph.uploaded_at,
    }



@router.get("/{file_id}/elements")
def get_file_stats(file_id: uuid.UUID, session: Session = Depends(get_session)):
    graph = session.get(Graph, file_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    subjects  = session.exec(
        select(Subject).select_from(Subject).where(Subject.graph_id == file_id)
    ).all()
    predicates = session.exec(
        select(Predicate).select_from(Predicate).where(Predicate.graph_id == file_id)
    ).all()
    objects   = session.exec(
        select(Object).select_from(Object).where(Object.graph_id == file_id)
    ).all()

    return {
        "graph_id":        str(graph.id),
        "subjects":        [s for s in subjects],
        "predicates":      [p for p in predicates],
        "objects":         [o for o in objects],
    }


@router.get("/{file_id}/visualise")
def visualise_graph(
    file_id: uuid.UUID,
    limit:   int = 200,           # cap for large graphs
    session: Session = Depends(get_session)
):
    graph = session.get(Graph, file_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found.")

    rdf_graph = rdflib.ConjunctiveGraph()
    try:
        rdf_graph.parse(graph.file_path, format=graph.format)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load graph: {exc}")

    if len(rdf_graph) > limit:
        limited = rdflib.ConjunctiveGraph()
        for i, triple in enumerate(rdf_graph):
            if i >= limit:
                break
            limited.add(triple)
        rdf_graph = limited

    cyto = graph_to_cytoscape(rdf_graph)

    return {
        "meta" : {
                    "graph_id":    str(file_id),
                    "name":        graph.name,
                    "node_count":  len(cyto["nodes"]),
                    "edge_count":  len(cyto["edges"]),
                    "truncated":   len(rdf_graph) >= limit,
            },
        "elements":    cyto["nodes"] + cyto["edges"]
    }