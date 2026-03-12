from typing import Optional,List,TYPE_CHECKING
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Relationship
from app.models.query_ontology import QueryOntology

if TYPE_CHECKING:
    from app.models.ontology import Ontology
    from app.models.rdf import Graph



class SparqlHistory(SQLModel, table=True):
    __tablename__ = "sparql_history"

    id: uuid.UUID           = Field(default_factory=uuid.uuid4, primary_key=True)
    query: str              = Field(nullable=False)
    query_type: str         = Field(nullable=False)
    graph_id: uuid.UUID     = Field(foreign_key="graphs.id", nullable=False)
    executed_at: datetime   = Field(default_factory=datetime.utcnow)

    graph: Optional["Graph"]  = Relationship(back_populates="sparql_history")
    ontologies: List["Ontology"] = Relationship(back_populates="sparql_queries", link_model=QueryOntology)


class SparqlQueryRequest(SQLModel):
    query: str
    graph_id: uuid.UUID