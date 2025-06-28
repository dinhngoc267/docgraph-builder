from typing import List

from pydantic_ai import Agent, RunContext, ModelRetry

from src.models import AgentName, Dependency, BaseMention, BaseRelation, DomainOntology
from src.agents.prompts import RELATION_EXTRACTION_PROMPT

from .._base import instruct_model


def create_relation_extraction_agent(
        relation_model,
        mention_strings,
        relation_types,
        constraints
) -> Agent[DomainOntology]:

    agent = Agent[DomainOntology](
        name=AgentName.relation_extraction_agent.value,
        model=instruct_model,
        system_prompt=RELATION_EXTRACTION_PROMPT.format(
            mention_strings=mention_strings,
            relation_types=relation_types,
            constraints=constraints),
        result_type=List[relation_model],
        retries=5,
    )

    @agent.output_validator
    async def validate_relation_constraint(
            ctx: RunContext[DomainOntology],
            list_relations: List[BaseRelation]
    ):

        for item in list_relations:
            try:
                subject = BaseMention.from_string(item.subject)
                subject_type = subject.entity_type
                object_ = BaseMention.from_string(item.object)
                object_type = object_.entity_type
                predicate = item.predicate

                if not ctx.deps.is_valid_relationship(subject_type, object_type, predicate):
                    raise ModelRetry(
                        f"Triplet {subject_type}-{predicate}->{object_type} is not a valid relationship type!")
                item.subject = subject.text
                item.object = object_.text

            except Exception as e:
                raise ModelRetry(f"{e}")

        return list_relations

    return agent
