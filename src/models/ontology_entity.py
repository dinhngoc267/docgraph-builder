from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from typing import ClassVar, List, Iterator, Optional
from itertools import count

class OntologyEntity(BaseModel, ABC):
    _id_counter: ClassVar[Iterator[int]] = count(1)

    id: str
    summary: str = Field(..., description="Summary description of the instance.")
    embedding: Optional[List[float]] = Field(None, description="The embedding vector.")

    @classmethod
    def next_id(cls) -> int:
        return next(cls._id_counter)

    @abstractmethod
    def node_label(self) -> str:
        """Returns the node label for this entity."""
        pass

    @classmethod
    def infer_relationship(cls, subject_label: str, object_label: str) -> str:
        """Centralized ontology relationship inference."""
        RELATIONSHIP_MAP = {
            ("Unit", "Mention"): "HAS_MENTION",
            ("Doc", "Unit"): "HAS_UNIT",
            ("Unit", "Unit"): "NEXT_UNIT",
        }
        return RELATIONSHIP_MAP.get((subject_label, object_label))

    def get_relationships(self) -> list:
        """By default, entities have no outgoing relationships."""
        return []