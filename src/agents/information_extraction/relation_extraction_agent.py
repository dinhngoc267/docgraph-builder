from typing import List

from pydantic_ai import Agent

from src.models import AgentName
from src.agents.prompts import RELATION_EXTRACTION_PROMPT

from .._base import ollama_model

def create_relation_extraction_agent(relation_model) -> Agent:
    agent = Agent(
        name=AgentName.relation_extraction_agent.value,
        model=ollama_model,
        system_prompt=RELATION_EXTRACTION_PROMPT,
        result_type=List[relation_model],
        retries=5,
    )

    return agent