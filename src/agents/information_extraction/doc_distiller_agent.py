from typing import Type

from pydantic import BaseModel
from pydantic_ai import Agent

from src.models import AgentName
from src.agents.prompts import DOC_DISTILLER_PROMPT

from .._base import ollama_model, tiny_model

def create_doc_distiller_agent(output_model, schema) -> Agent:
    agent = Agent(
        name=AgentName.doc_distiller_agent.value,
        model=tiny_model,
        system_prompt=DOC_DISTILLER_PROMPT.format(schema=schema),
        result_type=output_model,
        retries=5,
    )

    return agent