from typing import Optional, Generic, TypeVar, List, Any

from pydantic import BaseModel, Field

UnitT = TypeVar("UnitT")

class BaseDocUnit(BaseModel):
    title: Optional[str] = Field(None, description="The title of the paragraph.")
    text: str = Field(..., description="The text of the paragraph. Extracted from the document.")
    mentions: List[Any] = Field(None, description="List of mentions extracted from the document.")
    relationships: List[Any] = Field(None, description="List of relationships between mentions extracted from the document.")

class BaseDoc(BaseModel, Generic[UnitT]):
    title: Optional[str] = Field(None, description="The title of the document.")

    summary: str = Field(..., description="The summary of the document.")
    units: List[UnitT] = Field(..., description="The units of the document.")