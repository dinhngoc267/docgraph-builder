from typing import Type

from pydantic import BaseModel
from pydantic_ai import Agent

from src.models import AgentName
from src.agents.prompts import DOC_DISTILLER_PROMPT

from .._base import instruct_model

def create_doc_distiller_agent(output_model, schema) -> Agent:
    agent = Agent(
        name=AgentName.doc_distiller_agent.value,
        model=instruct_model,
        instructions=DOC_DISTILLER_PROMPT,
        result_type=output_model,
        retries=5,
    )

    return agent