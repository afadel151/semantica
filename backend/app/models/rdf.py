from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from typing import List, Optional,TYPE_CHECKING

import uuid

if TYPE_CHECKING:
    from app.models.sparql import SparqlHistory

class Graph(SQLModel, table=True):
    __tablename__ = "graphs"

    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str                       = Field(nullable=False)
    format: str                     = Field(nullable=False)
    file_name: str                  = Field(nullable=False)
    file_path: str                  = Field(nullable=False)
    file_size: int                  = Field(nullable=False)
    triples_count: int              = Field(nullable=False, default=0)
    uploaded_at: datetime           = Field(nullable=False, default_factory=datetime.utcnow)
    graph_type: str                 = Field(default="RDF", nullable=False)

    subjects:       List["Subject"]       = Relationship(back_populates="graph", cascade_delete=True)
    predicates:     List["Predicate"]     = Relationship(back_populates="graph", cascade_delete=True)
    objects:        List["Object"]        = Relationship(back_populates="graph", cascade_delete=True)
    sparql_history: List["SparqlHistory"] = Relationship(back_populates="graph", cascade_delete=True)


class Subject(SQLModel, table=True):
    __tablename__ = "subjects"

    id: uuid.UUID              = Field(default_factory=uuid.uuid4, primary_key=True)
    graph_id: uuid.UUID        = Field(foreign_key="graphs.id", nullable=False)
    uri: str                   = Field(nullable=False)
    prefix_form: Optional[str] = Field(default=None, nullable=True)
    rdf_type: Optional[str]    = Field(default=None, nullable=True)
    predicate_count: int       = Field(default=0)
    is_star: bool              = Field(default=False)

    graph: Optional[Graph]     = Relationship(back_populates="subjects")


class Predicate(SQLModel, table=True):
    __tablename__ = "predicates"

    id: uuid.UUID              = Field(default_factory=uuid.uuid4, primary_key=True)
    graph_id: uuid.UUID        = Field(foreign_key="graphs.id", nullable=False)
    uri: str                   = Field(nullable=False)
    prefix_form: Optional[str] = Field(default=None, nullable=True)
    usage_count: int           = Field(default=0)
    domain: Optional[str]      = Field(default=None, nullable=True)
    range: Optional[str]       = Field(default=None, nullable=True)

    graph: Optional[Graph]     = Relationship(back_populates="predicates")


class Object(SQLModel, table=True):
    __tablename__ = "objects"

    id: uuid.UUID              = Field(default_factory=uuid.uuid4, primary_key=True)
    graph_id: uuid.UUID        = Field(foreign_key="graphs.id", nullable=False)
    value: str                 = Field(nullable=False)
    kind: str                  = Field(nullable=False)
    prefix_form: Optional[str] = Field(default=None, nullable=True)
    datatype: Optional[str]    = Field(default=None, nullable=True)
    language: Optional[str]    = Field(default=None, nullable=True)
    referenced_by: int         = Field(default=0)
    is_star: bool              = Field(default=False)

    graph: Optional[Graph]     = Relationship(back_populates="objects")


