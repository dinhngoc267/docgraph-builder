import re

from pydantic import BaseModel, Field, model_validator
from typing import List


class EntityType(BaseModel):
    name: str = Field(..., description="The label or identifier for this entity type.")
    description: str = Field(..., description="A brief explanation of what this entity type represents.")

class BaseMention(BaseModel):
    entity_type: str
    text: str = Field(..., description="Mention string appears in the passage")

    def __str__(self):
        return f"<{self.entity_type}>{self.text}</{self.entity_type}>"

    @classmethod
    def from_string(cls, s: str):
        match = re.fullmatch(r"<(?P<etype>[^>]+)>(?P<text>.+)</\1>", s.strip())
        if not match:
            raise ValueError(f"Invalid mention string: {s}")
        return cls(entity_type=match.group("etype"), text=match.group("text"))


class TypePair(BaseModel):
    subject_type: str = Field(..., description="Entity type name acting as subject.")
    object_type: str = Field(..., description="Entity type name acting as object.")


class RelationshipType(BaseModel):
    name: str = Field(..., description="The name of the relationship type.")
    description: str = Field(..., description="Explanation of what this relationship represents.")

    allowed_type_pairs: List[TypePair] = Field(
        ...,
        description="A list of allowed (subject_type, object_type) pairs. Each type must be a name from the entity types defined in the ontology."
    )

class BaseRelation(BaseModel):
    subject: str = Field(..., description="Entity acting as subject.")
    object: str = Field(..., description="Entity acting as object.")
    predicate: str = Field(..., description="Relationship type from subject to object.")


class DomainOntology(BaseModel):
    domain_name: str = Field(..., description="The name of the domain.")
    entity_types: List[EntityType] = Field(..., description="Entities defined within the domain.")
    relationship_types: List[RelationshipType] = Field(...,
                                                       description="A list of all relationship types that describe possible connections between entity types in this domain.")


    def is_valid_relationship(self, subject_type: str, object_type: str, predicate: str) -> bool:
        for rel in self.relationship_types:
            if rel.name == predicate:
                return (subject_type, object_type) in {
                    (pair.subject_type, pair.object_type)
                    for pair in rel.allowed_type_pairs
                }

        return False


    @model_validator(mode="after")
    def validate_relationship_type(self):
        entity_names = {et.name for et in self.entity_types}
        for rel in self.relationship_types:
            for pair in rel.allowed_type_pairs:
                if pair.subject_type not in entity_names:
                    raise ValueError(
                        f"Invalid pair in relationship '{rel.name}': subject_type '{pair.subject_type}' "
                        f"is not in defined entity types {entity_names}. Full pair: ({pair.subject_type}, {pair.object_type})"
                    )
                if pair.object_type not in entity_names:
                    raise ValueError(
                        f"Invalid pair in relationship '{rel.name}': object_type '{pair.object_type}' "
                        f"is not in defined entity types {entity_names}. Full pair: ({pair.subject_type}, {pair.object_type})"
                    )
        return self
