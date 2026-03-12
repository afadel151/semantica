from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session
from typing import List
import uuid
from fastapi.responses import FileResponse
import csv
import json
import tempfile

from rdflib import Graph as RDFGraph

from app.core.db import get_session
from app.models.sparql import SparqlHistory, SparqlQueryRequest
from app.models.rdf import Graph

router = APIRouter(prefix="/sparql", tags=["sparql"])


# ----------------------------
# récupérer les requêtes récentes
# ----------------------------
@router.get("/recent", response_model=List[SparqlHistory])
def get_recent_queries(session: Session = Depends(get_session)):

    queries = session.exec(
        select(SparqlHistory)
        .order_by(SparqlHistory.executed_at.desc())
        .limit(10)
    ).all()

    return queries


# ----------------------------
# fonction interne pour exécuter SPARQL
# ----------------------------
def execute_sparql(query: str, graph_path: str):

    g = RDFGraph()
    g.parse(graph_path)

    results = g.query(query)

    data = []

    for row in results:
        data.append([str(x) for x in row])

    return data


# ----------------------------
# SELECT
# ----------------------------
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


# ----------------------------
# ASK
# ----------------------------
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

# ----------------------------
# DESCRIBE
# ----------------------------
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


# ----------------------------
# CONSTRUCT
# ----------------------------
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


# ----------------------------
# export (placeholder)
# ----------------------------
## Query ; ?format=(json||csv)&graph_id=graph_id&query=SELECT%20?s%20?p%20?o%20WHERE%20{%20?s%20?p%20?o%20}%20LIMIT%2010
@router.get("/export")
def export_result(
    query: str,
    graph_id: uuid.UUID,
    format: str = Query("json", enum=["json", "csv"]),
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

    # -------- EXPORT JSON --------
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

    # -------- EXPORT CSV --------
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
# ----------------------------
# supprimer requête
# ----------------------------
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
