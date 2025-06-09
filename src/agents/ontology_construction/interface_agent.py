import asyncio

from pydantic_ai import Agent, RunContext

from src.models import AgentName, Ontology
from src.agents.prompts import INTERFACE_AGENT_PROMPT

# from ._agent_registry import AgentRegistry
from src.agents._base import instruct_model


# @AgentRegistry.register(AgentName.ontology_init_agent)
def create_interface_agent() -> Agent:
    agent = Agent(
        name=AgentName.interface_agent.value,
        model=instruct_model,
        instructions=INTERFACE_AGENT_PROMPT,
        result_type=str,
        retries=5
    )

    return agent
