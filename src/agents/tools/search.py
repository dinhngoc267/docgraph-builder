from duckduckgo_search import DDGS
from pydantic_ai import RunContext


async def search(
        query: str
):
    print("Tool called: ", query)
    with DDGS() as ddgs:
        results = ddgs.text(query)
        print(results)
        return results

