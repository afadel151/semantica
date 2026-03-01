from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class SparqlHistory(Base):
    __tablename__ = "sparql_history"

    id          = Column(Integer,  primary_key=True, index=True)
    query       = Column(Text,     nullable=False)                   # texte de la requête
    query_type  = Column(String,   nullable=True)                    # "SELECT"|"ASK"|"CONSTRUCT"|"DESCRIBE"
    graph_id    = Column(Integer,  ForeignKey("graphs.id",     ondelete="SET NULL"), nullable=True, index=True)
    ontolgy_id  = Column(Integer,  ForeignKey("ontologies.id", ondelete="SET NULL"), nullable=True, index=True)
    executed_at = Column(DateTime, server_default=func.now())        # horodatage auto

   
    graph    = relationship("Graph",    back_populates="sparql_histories")
    ontology = relationship("Ontology", back_populates="sparql_histories")

    def __repr__(self):
        target = f"graph={self.graph_id}" if self.graph_id else f"ontology={self.ontolgy_id}"
        return f"<SparqlHistory id={self.id} type='{self.query_type}' {target}>"