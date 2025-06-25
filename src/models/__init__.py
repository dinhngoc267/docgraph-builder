from .enums import AgentName
from .deps import Dependency
from .domain_ontology import DomainOntology, BaseMention, BaseRelation
from .doc_schema import BaseDoc, BaseDocUnit

from ._utils import build_dynamic_relation_model, create_model_from_schema

from pydantic import BaseModel, Field

from typing import Optional

__all__ = [
    "DomainOntology",
    "AgentName",
    "HumanReview",
    "build_dynamic_relation_model",
    "create_model_from_schema",
    "Dependency",
    "BaseDoc",
    "BaseDocUnit",
    "BaseMention"
]

class HumanReview(BaseModel):
    is_agreed: bool = Field(..., description="Indicates whether the human reviewer agrees with the generated ontology.")
    feedback: Optional[str] = Field(description="Comments or suggestions from the human reviewer about the ontology.")

