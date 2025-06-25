from pydantic_ai import Agent, Tool, RunContext

from src.models import AgentName, DomainOntology
from src.agents.prompts import DOMAIN_ONTOLOGY_INIT_PROMPT
from src.agents._base import instruct_model
from src.agents.tools import search, retrieve_data

def create_domain_ontology_agent() -> Agent:
    agent = Agent(
        name=AgentName.domain_ontology_init_agent.value,
        model=instruct_model,
        result_type=DomainOntology,
        instructions=DOMAIN_ONTOLOGY_INIT_PROMPT,
        tools=[
            Tool(retrieve_data, takes_ctx=True),
            Tool(search, takes_ctx=False),
        ],
        retries=5,
    )

    return agent