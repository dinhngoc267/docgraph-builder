import re
import json
import time


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
    return None

from typing import TypeVar
from typing import Sequence, Callable, Awaitable

from pydantic_ai.usage import Usage
from tqdm import tqdm

import anyio


import anyio
from typing import Callable, Awaitable, Sequence, TypeVar, Optional

T = TypeVar("T")

import asyncio
import anyio
from typing import Callable, Awaitable, Sequence, TypeVar, Optional

T = TypeVar("T")

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

