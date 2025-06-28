import re
import json
import time
import builtins

from pydantic import BaseModel, Field
from typing import Callable, Awaitable, Sequence, TypeVar, Optional, List , Type
from src.models import AgentName, Dependency, BaseDoc, BaseDocUnit, BaseRelation
from src.models.ontology_entity import OntologyEntity
T = TypeVar("T")

import asyncio
import anyio
from typing import Callable, Awaitable, Sequence, TypeVar, Optional


def extract_python_code_block(text: str) -> str:
    match = re.search(r"```python\s*([\s\S]+?)\s*```", text)
    if not match:
        raise ValueError("No valid ```python code block``` found in LLM output.")
    return match.group(1).strip()

def extract_json_from_markdown(markdown_string):
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', markdown_string)
    if match:
        json_string = match.group(1).strip()
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print("Invalid JSON found.")
            return e
    return None

async def task_group_gather(tasks: Sequence[Callable[[], Awaitable[T]]],
                            timeout_seconds: 120) -> list[Optional[T]]:
    results: list[Optional[T]] = [None] * len(tasks)
    max_retries = 5

    async def _run_task(task_fn: Callable[[], Awaitable[T]], index: int):
        for attempt in range(max_retries + 1):
            try:
                result = await asyncio.wait_for(task_fn(), timeout=timeout_seconds)
                results[index] = result
                return
            except asyncio.TimeoutError:
                print(f"Task {index} timed out on attempt {attempt + 1}")
            except Exception as e:
                print(f"Task {index} failed with error: {e}")
                return
        print(f"Task {index} failed after {max_retries + 1} attempts")

    async with anyio.create_task_group() as tg:
        for i, task_fn in enumerate(tasks):
            tg.start_soon(_run_task, task_fn, i)

    return results


def load_extended_models(code: str) -> tuple[Type[BaseDoc], Type[BaseDocUnit]]:
    safe_globals = {
        "BaseRelation": BaseRelation,
        "OntologyEntity": OntologyEntity,
        "BaseDocUnit": BaseDocUnit,
        "BaseDoc": BaseDoc,
        "Field": Field,
        "BaseModel": BaseModel,
        "Optional": Optional,
        "List": List,
        "__builtins__": builtins.__dict__,
    }

    local_env = {}
    try:
        exec(code, safe_globals, local_env)
    except Exception as e:
        raise RuntimeError(f"Error while executing LLM-generated code:\n{e}")

    # Extract the two classes
    ExtendedDocUnit = local_env.get("ExtendedDocUnit")
    ExtendedDoc = local_env.get("ExtendedDoc")

    if not ExtendedDocUnit or not ExtendedDoc:
        raise ValueError("Missing ExtendedDocUnit or ExtendedDoc in output.")

    return ExtendedDoc, ExtendedDocUnit


