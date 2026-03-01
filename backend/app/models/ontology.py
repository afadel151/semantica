from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class Ontology(Base):
  
    __tablename__ = "ontologies"

    id                = Column(Integer, primary_key=True, index=True)
    name              = Column(String,  nullable=False)              # ex: "FOAF Ontology"
    format            = Column(String,  nullable=True)               # "xml" | "turtle" | "n3"
    file_name         = Column(String,  nullable=True)               # ex: foaf.owl
    file_path         = Column(String,  nullable=True)               # chemin disque
    file_size         = Column(Integer, nullable=True)               # taille en octets
    classes_count     = Column(Integer, nullable=True, default=0)    # nb de classes extraites
    properties_count  = Column(Integer, nullable=True, default=0)    # nb de propriétés
    individuals_count = Column(Integer, nullable=True, default=0)    # nb d'individus
    uploaded_at       = Column(DateTime, server_default=func.now())  # date d'import

    # ── Relations ──────────────────────────────────────────────
    classes          = relationship("OntologyClass",    back_populates="ontology", cascade="all, delete-orphan")
    properties       = relationship("OntologyProperty", back_populates="ontology", cascade="all, delete-orphan")
    individuals      = relationship("Individual",       back_populates="ontology", cascade="all, delete-orphan")
    sparql_histories = relationship("SparqlHistory",    back_populates="ontology")

    def __repr__(self):
        return f"<Ontology id={self.id} name='{self.name}' classes={self.classes_count}>"


class OntologyClass(Base):
    __tablename__ = "classes"

    id             = Column(Integer, primary_key=True, index=True)
    ontology_id    = Column(Integer, ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False, index=True)
    uri            = Column(String,  nullable=False)             # URI complète
    label          = Column(String,  nullable=True)              # ex: "Person"
    prefix_form    = Column(String,  nullable=True)              # ex: foaf:Person
    parent_uri     = Column(String,  nullable=True)              # URI de la classe parente
    children_count = Column(Integer, nullable=True, default=0)   # nb de sous-classes
    is_abstract    = Column(Boolean, nullable=True, default=False) # classe abstraite ?
    depth          = Column(Integer, nullable=True, default=0)   # niveau dans l'arbre

    # ── Relation ───────────────────────────────────────────────
    ontology = relationship("Ontology", back_populates="classes")

    def __repr__(self):
        return f"<OntologyClass id={self.id} uri='{self.prefix_form or self.uri}' depth={self.depth}>"


class OntologyProperty(Base):
    __tablename__ = "properties"

    id          = Column(Integer, primary_key=True, index=True)
    ontology_id = Column(Integer, ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False, index=True)
    uri         = Column(String,  nullable=False)   # URI complète
    label       = Column(String,  nullable=True)    # ex: "knows"
    prefix_form = Column(String,  nullable=True)    # ex: foaf:knows
    type        = Column(String,  nullable=True)    # "ObjectProperty" | "DatatypeProperty"
    domain      = Column(String,  nullable=True)    # classe du sujet    (ex: foaf:Person)
    range       = Column(String,  nullable=True)    # classe de l'objet  (ex: xsd:string)

    # ── Relation ───────────────────────────────────────────────
    ontology = relationship("Ontology", back_populates="properties")

    def __repr__(self):
        return f"<OntologyProperty id={self.id} uri='{self.prefix_form or self.uri}' type='{self.type}'>"


class Individual(Base):
    
    __tablename__ = "individuals"

    id             = Column(Integer, primary_key=True, index=True)
    ontology_id    = Column(Integer, ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False, index=True)
    uri            = Column(String,  nullable=False)           # URI complète
    label          = Column(String,  nullable=True)            # ex: "TheDarkSideOfTheMoon"
    prefix_form    = Column(String,  nullable=True)            # ex: ex:TheDarkSideOfTheMoon
    rdf_type       = Column(String,  nullable=True)            # ex: schema:MusicAlbum
    property_count = Column(Integer, nullable=True, default=0) # nb de propriétés

    # ── Relation ───────────────────────────────────────────────
    ontology = relationship("Ontology", back_populates="individuals")

    def __repr__(self):
        return f"<Individual id={self.id} uri='{self.prefix_form or self.uri}' type='{self.rdf_type}'>"