from .ontology import Ontology, SchemaDesign
from .enums import AgentName
from .deps import MyDeps
from ._utils import build_dynamic_relation_model, create_model_from_schema

from pydantic import BaseModel, Field

from typing import Optional

__all__ = [
    "Ontology",
    "AgentName",
    "HumanReview",
    "SchemaDesign",
    "build_dynamic_relation_model",
    "create_model_from_schema",
    "MyDeps"
]

class HumanReview(BaseModel):
    is_agreed: bool = Field(..., description="Indicates whether the human reviewer agrees with the generated ontology.")
    feedback: Optional[str] = Field(description="Comments or suggestions from the human reviewer about the ontology.")

