from pydantic import BaseModel
from enum import Enum

class AgentName(str, Enum):
    domain_ontology_init_agent = "domain_ontology_init_agent"
    interface_agent = "interface_agent"
    human_preference_agent = "human_preference_agent"
    doc_schema_design_agent = "doc_schema_design_agent"
    doc_schema_generation_agent = "doc_schema_generation_agent"

    doc_distiller_agent = "doc_distiller_agent"
    mention_detection_agent = "mention_detection_agent"
    relation_extraction_agent = "relation_extraction_agent"