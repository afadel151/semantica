from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Ontology(SQLModel, table=True):
    __tablename__ = "ontologies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    format: str
    file_name: str
    file_path: str
    file_size: int
    classes_count: int = 0
    properties_count: int = 0
    individuals_count: int = 0
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class OntologyClass(SQLModel, table=True):
    __tablename__ = "classes"

    id: Optional[int] = Field(default=None, primary_key=True)
    ontology_id: int = Field(foreign_key="ontologies.id")
    uri: str
    label: Optional[str] = None
    prefix_form: Optional[str] = None
    parent_uri: Optional[str] = None
    children_count: int = 0
    is_abstract: bool = False
    depth: int = 0


class OntologyProperty(SQLModel, table=True):
    __tablename__ = "properties"

    id: Optional[int] = Field(default=None, primary_key=True)
    ontology_id: int = Field(foreign_key="ontologies.id")
    uri: str
    label: Optional[str] = None
    prefix_form: Optional[str] = None
    type: Optional[str] = None        # owl:ObjectProperty | owl:DatatypeProperty
    domain: Optional[str] = None
    range: Optional[str] = None


class Individual(SQLModel, table=True):
    __tablename__ = "individuals"

    id: Optional[int] = Field(default=None, primary_key=True)
    ontology_id: int = Field(foreign_key="ontologies.id")
    uri: str
    label: Optional[str] = None
    prefix_form: Optional[str] = None
    rdf_type: Optional[str] = None
    property_count: int = 0