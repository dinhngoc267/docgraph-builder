from pydantic import BaseModel
from enum import Enum

class AgentName(str, Enum):
    ontology_init_agent: str = "ontology_init_agent"
    interface_agent: str = "interface_agent"
    human_preference_agent: str = "human_preference_agent"
    schema_design_agent: str = "schema_design_agent"
    schema_generation_agent: str = "schema_generation_agent"

    doc_distiller_agent: str = "doc_distiller_agent"
    mention_detection_agent: str = "mention_detection_agent"
    relation_extraction_agent: str = "relation_extraction_agent"