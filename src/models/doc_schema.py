from typing import Optional, Generic, TypeVar, List, Any
from pydantic import BaseModel, Field

from . import BaseMention, BaseRelation
from .ontology_entity import OntologyEntity

class RelationshipInstance(BaseModel):
    type_ : str
    subject_id: str
    object_id: str
    properties: dict = {}

class BaseDocUnit(OntologyEntity):
    id: Optional[str] = Field(None, description="The id of the document.")

    title: Optional[str] = Field(None, description="The title of the paragraph.")
    text: str = Field(..., description="The text of the paragraph. Extracted from the document.")

    mentions: Optional[List[BaseMention]] = Field([], description="Default is empty")
    relationships: Optional[List[BaseRelation]] = Field(
        [],
        description="Default is empty",
    )

    def model_post_init(self, context: Any, /) -> None:
        if self.id is None:
            self.id = f"Unit_{str(self.next_id()).zfill(4)}"

    def node_label(self) -> str:
        return "Unit"

    def get_relationships(self) -> list:
        rels = []
        for mention in self.mentions:
            rels.append(
                RelationshipInstance(
                    type_=self.infer_relationship(self.node_label(), mention.node_label()),
                    subject_id=self.id,
                    object_id=mention.id,
                )
            )

        if self.relationships:
            for relationship in self.relationships:
                rels.append(
                    RelationshipInstance(
                        type_=relationship.predicate.replace(" ", "_"),
                        subject_id=relationship.subject,
                        object_id=relationship.object,
                    )
                )

        return rels

UnitT = TypeVar("UnitT")

class BaseDoc(OntologyEntity, Generic[UnitT]):
    id: Optional[str] = Field(None, description="The id of the document.")
    title: Optional[str] = Field(None, description="The title of the document.")
    units: List[UnitT] = Field(..., description="The units of the document.")

    def node_label(self) -> str:
        return "Doc"

    def model_post_init(self, context: Any, /) -> None:
        if self.id is None:
            self.id = f"Doc_{str(self.next_id()).zfill(4)}"

    def get_relationships(self) -> list:
        rels = []
        for unit in self.units:
            rels.append(
                RelationshipInstance(
                    type_=self.infer_relationship(self.node_label(), unit.node_label()),
                    subject_id=self.id,
                    object_id=unit.id,
                )
            )

        for i in range(len(self.units) - 1):
            current_id = self.units[i].id
            next_id = self.units[i + 1].id

            rels.append(
                RelationshipInstance(
                    type_=self.infer_relationship(self.units[i].node_label(), self.units[i-1].node_label()),
                    subject_id=current_id,
                    object_id=next_id,
                )
            )

        return rels
