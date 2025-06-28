from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext, End
from rich.prompt import Prompt

from src.models import (
    HumanReview,
    DomainOntology,
    Dependency,
    BaseDoc,
    BaseDocUnit
)

from src.agents import (
    create_domain_ontology_agent,
    create_interface_agent,
    create_human_preference_agent,
    create_schema_design_agent,
    create_schema_generation_agent,
)

from src.agents.tools import (
    select_sample_data
)

from src.nodes.information_extraction_node import InformationExtractionNode
from src._utils import load_extended_models, extract_python_code_block

interface_agent = create_interface_agent()
human_preference_agent = create_human_preference_agent()
schema_design_agent = create_schema_design_agent()
schema_generation_agent = create_schema_generation_agent()


@dataclass
class DocSchemaDesignNode(BaseNode):
    data_dir: str
    domain_ontology: DomainOntology
    schema_output_path: str

    def save_schema_output(self, python_schema: str):
        import json
        save_obj = {
            "schema_code": python_schema
        }

        with open(self.schema_output_path, "w", encoding="utf-8") as f:
            json.dump(save_obj, f, ensure_ascii=False, indent=4)

    async def run(self, ctx: GraphRunContext[None, Dependency]) -> InformationExtractionNode:

        messages = []
        # Step 1. Pick a data sample
        sample_data: str = select_sample_data(self.data_dir)
        while True:
            # Step 2: Run schema design agent
            schema_design_result = await schema_design_agent.run(
                user_prompt=f"Document sample: {sample_data}\n"
                            "\n=============\n"
                            f"Ontology: {str(self.domain_ontology)}" if len(messages) == 0 else None,
                message_history=messages,
            )

            python_schema = extract_python_code_block(schema_design_result.output)
            ExtendedDoc, ExtendedDocUnit = load_extended_models(python_schema)
            # Step 2.b Save the model into .json files.
            self.save_schema_output(python_schema)

            # Step 3: Ask user for their confirmation or review
            interface_response_result = await interface_agent.run(
                user_prompt=f" {str(ExtendedDocUnit.model_json_schema())}\n {str(ExtendedDoc.model_json_schema())}"
            )
            user_response = Prompt.ask(interface_response_result.output)

            # Step 4: Parse user intention
            human_review = await human_preference_agent.run(
                user_prompt=user_response,
                message_history=messages
            )

            review: HumanReview = human_review.output

            if review.is_agreed:  # Break loop when reviewer agrees
                break
            else:
                messages += human_review.new_messages()

        ExtendedDoc: BaseDoc = ExtendedDoc

        return InformationExtractionNode(data_dir=self.data_dir,
                                         domain_ontology=self.domain_ontology,
                                         doc_schema=ExtendedDoc)
