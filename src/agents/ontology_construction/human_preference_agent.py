import asyncio

from pydantic_ai import Agent, RunContext

from src.models import AgentName, HumanReview
from src.agents.prompts import HUMAN_PREFERENCE_PROMPT

from src.agents._base import ollama_model


# @AgentRegistry.register(AgentName.ontology_init_agent)
def create_human_preference_agent() -> Agent:
    agent = Agent(
        name=AgentName.human_preference_agent.value,
        model=ollama_model,
        instructions=HUMAN_PREFERENCE_PROMPT,
        result_type=HumanReview,
        retries=5,
        model_settings={"temperature": 0}
    )

    return agent
