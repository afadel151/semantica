from fastapi import APIRouter
from sqlmodel import select, delete, func, col
from typing import Any, List

router = APIRouter(prefix="/sparql", tags=["sparql"])
# request and response models will be available at app/models/sparql.py

# get recent queries 
@router.get('/recent')
def get_recent_queries():
    return 

# run a new request (using the active graph and ontology)
# select query
@router.post('/select')
def run_select():
    return

# ask query
@router.post('/ask')
def run_ask():
    return

# describe query
@router.post('/describe')
def run_describe():
    return


# construct query
@router.post('/construct')
def run_construct():
    return

# export result (May be moved to frontend)
@router.get('/export')
def export_result():
    return

# delete query
@router.delete('/{query_id}')
def delete_query():
    return