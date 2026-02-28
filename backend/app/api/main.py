from fastapi import APIRouter
from app.api.v1.routes import ontology,rdf,sparql
api_router = APIRouter()


api_router.include_router(rdf.router)
api_router.include_router(ontology.router)
api_router.include_router(sparql.router)
