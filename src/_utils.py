import re
import json

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


T = TypeVar("T")

async def task_group_gather(tasks: Sequence[Callable[[], Awaitable[T]]]):

    results: list[T] = [None] * len(tasks)
    print('len result', len(results))

    async def _run_task(tsk: Callable[[], Awaitable[T]], index: int):
        """Helper function to run a task and store the result in the correct index."""
        results[index] = await tsk()

    async with anyio.create_task_group() as tg:
        for i, task in enumerate(tasks):
            tg.start_soon(_run_task, task, i)

    return results