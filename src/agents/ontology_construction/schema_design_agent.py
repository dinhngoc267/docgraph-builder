import json
import re

from pydantic_ai import Agent

from src.models import AgentName
from src.agents.prompts import SCHEMA_DESIGN_PROMPT

# from ._agent_registry import AgentRegistry
from src.agents._base import instruct_model


def extract_json_from_markdown(markdown_string):
    """Extracts JSON from a Markdown string.

    Args:
        markdown_string: The Markdown string containing JSON.

    Returns:
        A Python dictionary or None if no JSON is found.
    """
    # Regular expression to find JSON within code blocks
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', markdown_string)
    if match:
        json_string = match.group(1).strip()
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print("Invalid JSON found.")
            return e
    return


def create_schema_design_agent() -> Agent:
    agent = Agent(
        name=AgentName.schema_design_agent.value,
        model=instruct_model,
        instructions=SCHEMA_DESIGN_PROMPT,
        result_type=str,
        retries=5,
        model_settings={"temperature": 0}
    )


    return agent

