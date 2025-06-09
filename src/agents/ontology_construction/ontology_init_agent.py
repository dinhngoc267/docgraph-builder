from pydantic_ai import Agent, Tool, RunContext

from src.models import AgentName, Ontology
from src.agents.prompts import ONTOLOGY_INIT_PROMPT

# from ._agent_registry import AgentRegistry
from src.agents._base import instruct_model
from src.agents.tools.search import search
from src.agents.tools.select_sample_data import retrieve_data


# @AgentRegistry.register(AgentName.ontology_init_agent)
def create_ontology_init_agent() -> Agent:
    agent = Agent(
        name=AgentName.ontology_init_agent.value,
        model=instruct_model,
        result_type=Ontology,
        instructions=ONTOLOGY_INIT_PROMPT,
        tools=[
            Tool(retrieve_data, takes_ctx=True),
            Tool(search, takes_ctx=False),
        ],
        retries=5,
        model_settings={"temperature": 0}

    )

    return agent

# async def main():
#
#     import json
#
#     interface_agent = create_interface_agent()
#     ontology_init_agent = create_ontology_init_agent()
#
#     data = json.load(open("/home/ju/PycharmProjects/docgraph-construction/notebooks/history_textbook.json"))
#
#     sample = "Title: Những năm đầu của cuộc kháng chiến toàn quốc chống thực dân Pháp (1946 - 1950)"
#
#     for i,(key, value) in enumerate(data['Lớp 12']['Việt Nam từ năm 1945 đến năm 1954']['Những năm đầu của cuộc kháng chiến toàn quốc chống thực dân Pháp (1946 - 1950)'].items()):
#         sample += f"\n{str(i)} {key}\n{value}"
#
#     result = await ontology_init_agent.run(sample)
#
#     print(result.output)
#
# asyncio.run(main())