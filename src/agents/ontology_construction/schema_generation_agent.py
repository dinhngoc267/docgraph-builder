import json
import re

from pydantic_ai import Agent, RunContext, ModelRetry

from src.models import AgentName
from src.agents.prompts import SCHEMA_GENERATION_PROMPT

# from ._agent_registry import AgentRegistry
from src.agents._base import coder_model
from src.models._utils import create_model_from_schema




# @AgentRegistry.register(AgentName.ontology_init_agent)
def create_schema_generation_agent() -> Agent:
    agent = Agent(
        name=AgentName.schema_generation_agent.value,
        model=coder_model,
        instructions=SCHEMA_GENERATION_PROMPT,
        result_type=str,
        retries=5,
        model_settings={"temperature": 0}
    )

    @agent.output_validator
    async def validate_schema(_: RunContext, output: str) -> str:
        try:
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', output)
            json_string = match.group(1).strip()
            schema =json.loads(json_string)

            doc_model = create_model_from_schema(schema,"Doc")
            doc_unit_model = create_model_from_schema(schema, "DocUnit")

            if 'units' not in doc_model.model_fields:
                raise ModelRetry("The model 'Doc' should have an attribute 'units' instead")
            return output
        except Exception as e:
            raise ModelRetry(f"Invalid json schema: {e}")

    return agent

