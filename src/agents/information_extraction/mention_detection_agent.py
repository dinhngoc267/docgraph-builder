from typing import Type, List

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ModelRetry
import re

from src.models import AgentName, create_model_from_schema, build_dynamic_relation_model
from src.agents.prompts import MENTION_DETECTION_PROMPT

from .._base import instruct_model

def create_mention_detection_agent(mention_model, entity_types) -> Agent:
    agent = Agent(
        name=AgentName.mention_detection_agent.value,
        model=instruct_model,
        system_prompt=MENTION_DETECTION_PROMPT.format(entity_types=entity_types),
        result_type=List[mention_model],
        retries=5,
    )

    # @agent.output_validator
    # async def validate_schema(_: RunContext, output: List) -> str:
    #     if len(output) > 0:
    #         return output
    #     else:
    #         raise ModelRetry(f"Output shouldn't be empty list")
        # except Exception as e:
        #     raise ModelRetry(f"Invalid json schema: {e}")

    return agent