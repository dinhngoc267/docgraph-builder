from typing import List

from pydantic_ai import Agent

from src.models import AgentName
from src.agents.prompts import RELATION_EXTRACTION_PROMPT

from .._base import instruct_model

def create_relation_extraction_agent(relation_model, mention_strings, relation_types) -> Agent:
    agent = Agent(
        name=AgentName.relation_extraction_agent.value,
        model=instruct_model,
        system_prompt=RELATION_EXTRACTION_PROMPT.format(mention_strings=mention_strings, relation_types=relation_types),
        result_type=List[relation_model],
        retries=5,
    )

    return agent