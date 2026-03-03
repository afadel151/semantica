from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class SPARQLHistory(SQLModel, table=True):
    __tablename__ = "sparql_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    query: str
    query_type: str
    graph_id: Optional[int] = Field(default=None, foreign_key="graphs.id")
    executed_at: datetime = Field(default_factory=datetime.utcnow)



class QueryOntology(SQLModel, table=True):
    __tablename__ = "query_ontologies"

    query_id: int = Field(foreign_key="sparql_history.id", primary_key=True)
    ontology_id: int = Field(foreign_key="ontologies.id", primary_key=True)