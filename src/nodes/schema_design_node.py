from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext, End

from src.models import (
    HumanReview,
    Ontology
)

from src.agents import (
    create_ontology_init_agent,
    create_interface_agent,
    create_human_preference_agent,
    create_schema_design_agent,
    create_schema_generation_agent,
)

from src.agents.tools import (
    select_sample_data
)

from src.nodes.information_extraction_node import InformationExtractionNode
from src._utils import extract_json_from_markdown

interface_agent = create_interface_agent()
human_preference_agent = create_human_preference_agent()
schema_design_agent = create_schema_design_agent()
schema_generation_agent = create_schema_generation_agent()



@dataclass
class SchemaDesignNode(BaseNode):
    data_dir: str
    ontology: Ontology

    async def run(self, ctx: GraphRunContext) -> InformationExtractionNode:

        messages = []
        while True:
            # Step 1. Pick a data sample
            sample_data: str = select_sample_data(self.data_dir)

            # Step 2: Run schema design agent
            schema_design_result = await schema_design_agent.run(
                user_prompt=f"Document sample: {sample_data}\n"
                            "\n=============\n"
                            f"Ontology: {str(self.ontology)}",
            )

            messages += schema_design_result.new_messages()

            # Step 3: Ask user for their confirmation or review
            interface_response_result = await interface_agent.run(
                user_prompt=""
                f" {str(schema_design_result.output).replace('<think>','').replace('</think>','')}"
            )

            print(interface_response_result.output)

            user_response = "I confirm"

            # Step 4: Parse user intention
            human_review = await human_preference_agent.run(
                user_prompt=user_response,
                message_history=messages
            )

            review: HumanReview = human_review.output

            if review.is_agreed: # Break loop when reviewer agree
                break
            else:
                messages += human_review.new_messages()

        final_schema_json = await schema_generation_agent.run(
            user_prompt=str(schema_design_result.output)
        )

        return InformationExtractionNode(data_dir=self.data_dir, schema=extract_json_from_markdown(final_schema_json.output))


