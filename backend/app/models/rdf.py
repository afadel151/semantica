from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Graph(SQLModel, table=True):
    __tablename__ = "graphs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    format: str
    file_name: str
    file_path: str
    file_size: int
    triples_count: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class Subject(SQLModel, table=True):
    __tablename__ = "subjects"

    id: Optional[int] = Field(default=None, primary_key=True)
    graph_id: int = Field(foreign_key="graphs.id")
    uri: str
    prefix_form: Optional[str] = None
    rdf_type: Optional[str] = None
    predicate_count: int = 0


class Predicate(SQLModel, table=True):
    __tablename__ = "predicates"

    id: Optional[int] = Field(default=None, primary_key=True)
    graph_id: int = Field(foreign_key="graphs.id")
    uri: str
    prefix_form: Optional[str] = None
    usage_count: int = 0
    domain: Optional[str] = None
    range: Optional[str] = None


class RDFObject(SQLModel, table=True):
    __tablename__ = "objects"

    id: Optional[int] = Field(default=None, primary_key=True)
    graph_id: int = Field(foreign_key="graphs.id")
    value: str
    kind: str                         # literal | uri | blank
    prefix_form: Optional[str] = None
    datatype: Optional[str] = None
    language: Optional[str] = None
    referenced_by: Optional[int] = None