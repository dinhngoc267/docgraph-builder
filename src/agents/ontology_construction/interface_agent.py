from pydantic_ai import Agent

from src.models import AgentName
from src.agents.prompts import INTERFACE_AGENT_PROMPT

from src.agents._base import instruct_model


def create_interface_agent() -> Agent:
    agent = Agent(
        name=AgentName.interface_agent.value,
        model=instruct_model,
        instructions=INTERFACE_AGENT_PROMPT,
        result_type=str,
        retries=5
    )

    return agent
