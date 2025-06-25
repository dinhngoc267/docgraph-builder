import json
import re
import builtins

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelRetry

from src.models import AgentName, Dependency, BaseDoc, BaseDocUnit
from src.agents.prompts import DOCUMENT_SCHEMA_DESIGN_PROMPT
from src.agents._base import instruct_model
from src._utils import extract_json_from_markdown, load_extended_models, extract_python_code_block
from typing import Any, Dict, Optional, List, Type


def create_schema_design_agent() -> Agent:
    agent = Agent(
        name=AgentName.doc_schema_design_agent.value,
        model=instruct_model,
        system_prompt=DOCUMENT_SCHEMA_DESIGN_PROMPT,
        result_type=str,
        retries=5,
    )

    @agent.output_validator
    async def validate_output_models(ctx: RunContext[Dependency], output_models: str):
        try:
            clean_code = extract_python_code_block(output_models)
            _ = load_extended_models(clean_code)
            return output_models
        except Exception as e:
            raise ModelRetry(f"Invalid python code: {e}")


    return agent

