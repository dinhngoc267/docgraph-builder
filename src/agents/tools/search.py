from duckduckgo_search import DDGS
from pydantic_ai import RunContext


async def search(
        query: str
):
    with DDGS() as ddgs:
        try:
            results = ddgs.text(query)
            return results
        except Exception as e:
            return "No results found"
