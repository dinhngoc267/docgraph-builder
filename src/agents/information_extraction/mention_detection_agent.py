from typing import Type, List

from pydantic import BaseModel
from pydantic_ai import Agent

from src.models import AgentName, create_model_from_schema, build_dynamic_relation_model
from src.agents.prompts import MENTION_DETECTION_PROMPT

from .._base import instruct_model

def create_mention_detection_agent(mention_model) -> Agent:
    agent = Agent(
        name=AgentName.mention_detection_agent.value,
        model=instruct_model,
        system_prompt=MENTION_DETECTION_PROMPT,
        result_type=List[mention_model],
        retries=5,
    )

    return agent