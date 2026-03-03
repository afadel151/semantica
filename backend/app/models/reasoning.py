from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class ReasoningResult(SQLModel, table=True):
    __tablename__ = "reasoning_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    graph_id: Optional[int] = Field(default=None, foreign_key="graphs.id")
    ontology_id: Optional[int] = Field(default=None, foreign_key="ontologies.id")
    reasoner: str                     # pellet | hermit | owlrl
    inferred_triples: int = 0
    executed_at: datetime = Field(default_factory=datetime.utcnow)