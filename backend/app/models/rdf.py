import uuid
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class Graph(Base):
    
    __tablename__ = "graphs"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String,  nullable=False)              # nom affiché
    format        = Column(String,  nullable=True)               # "turtle" || "xml" || "nt" || "jsonld"…
    file_name     = Column(String,  nullable=True)               # nom original du fichier
    file_path     = Column(String,  nullable=True)               # chemin sur le disque
    file_size     = Column(Integer, nullable=True)               # taille en octets
    triples_count = Column(Integer, nullable=True, default=0)    # nb total de triplets
    uploaded_at   = Column(DateTime, server_default=func.now())  # date d'import

    
    subjects         = relationship("Subject",      back_populates="graph", cascade="all, delete-orphan")
    predicates       = relationship("Predicate",    back_populates="graph", cascade="all, delete-orphan")
    objects          = relationship("RDFObject",    back_populates="graph", cascade="all, delete-orphan")
    sparql_histories = relationship("SparqlHistory", back_populates="graph")

    def __repr__(self):
        return f"<Graph id={self.id} name='{self.name}' triples={self.triples_count}>"


class Subject(Base):
    
    __tablename__ = "subjects"

    id              = Column(Integer, primary_key=True, index=True)
    graph_id        = Column(Integer, ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False, index=True)
    uri             = Column(String,  nullable=False)             # URI complète
    prefix_form     = Column(String,  nullable=True)              # ex: ex:Alice
    rdf_type        = Column(String,  nullable=True)              # annonyme ou classe RDF 
    predicate_count = Column(Integer, nullable=True, default=0)   # nb de propriétés

    
    graph = relationship("Graph", back_populates="subjects")

    def __repr__(self):
        return f"<Subject id={self.id} uri='{self.prefix_form or self.uri}'>"


class Predicate(Base):
    __tablename__ = "predicates"

    id          = Column(Integer, primary_key=True, index=True)
    graph_id    = Column(Integer, ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False, index=True)
    uri         = Column(String,  nullable=False)             # URI complète
    prefix_form = Column(String,  nullable=True)              # ex: foaf:knows
    usage_count = Column(Integer, nullable=True, default=0)   # nb d'utilisations
    domain      = Column(String,  nullable=True)              # classe attendue pour le sujet
    range       = Column(String,  nullable=True)              # classe attendue pour l'objet

   
    graph = relationship("Graph", back_populates="predicates")

    def __repr__(self):
        return f"<Predicate id={self.id} uri='{self.prefix_form or self.uri}' usage={self.usage_count}>"


class RDFObject(Base):
    
    __tablename__ = "objects"

    id            = Column(Integer, primary_key=True, index=True)
    graph_id      = Column(Integer, ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False, index=True)
    value         = Column(String,  nullable=False)   # la valeur brute ou URI
    kind          = Column(String,  nullable=False)   # "uri" | "literal" 
    prefix_form   = Column(String,  nullable=True)    #  (seulement si kind="uri")
    datatype      = Column(String,  nullable=True)    # xsd:integer, xsd:date… (si littéral typé)
    language      = Column(String,  nullable=True)    # "fr", "en"… (si littéral avec langue)
    referenced_by = Column(Integer, nullable=True)    # id du Subject source (optionnel)

    graph = relationship("Graph", back_populates="objects")

    def __repr__(self):
        return f"<RDFObject id={self.id} kind='{self.kind}' value='{self.value[:40]}'>"