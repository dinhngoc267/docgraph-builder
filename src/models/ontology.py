from pydantic import BaseModel, Field

from typing import List, Literal


class EntityType(BaseModel):
    name: str = Field(...,
                      description="The label or identifier for this entity type (e.g., ORGANIZATION, PERSON, LOCATION,...)")
    description: str = Field(..., description="A brief explanation of what this entity type represents")


class Ontology(BaseModel):
    domain_name: str = Field(...,
                             description="The name of the domain this ontology belongs to (e.g., HISTORICAL, LAW, MEDICAL,..)")
    entity_types: List[EntityType] = Field(...,
                                           description="A list of entity types defined within this domain")

class SchemaDesign(BaseModel):
    distill_technique: Literal["Segmentation", "Chunking"]
    schema: str = Field(..., description="Python script")