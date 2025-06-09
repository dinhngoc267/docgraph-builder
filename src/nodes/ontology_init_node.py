from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext, End

from src.models import HumanReview, MyDeps

from src.agents import (
    create_ontology_init_agent,
    create_interface_agent,
    create_human_preference_agent,
)

from src.agents.tools import (
    select_sample_data,
    retrieve_data
)

from src.nodes.schema_design_node import SchemaDesignNode

ontology_init_agent = create_ontology_init_agent()
interface_agent = create_interface_agent()
human_preference_agent = create_human_preference_agent()


@dataclass
class OntologyInitNode(BaseNode):
    data_dir: str

    async def run(self, ctx: GraphRunContext) -> SchemaDesignNode:

        messages = []
        deps = MyDeps(data_dir=self.data_dir)
        sample_data = select_sample_data(data_dir=self.data_dir)
        print("Sample data: {}".format(sample_data))
        while True:
            ontology_result = await ontology_init_agent.run(
                user_prompt=None if messages is None else sample_data,
                message_history=messages,
                deps=deps,
            )

            messages += ontology_result.new_messages()

            interface_response = await interface_agent.run(f"{str(ontology_result.output)}")
            messages += interface_response.new_messages()

            print(interface_response.output)

            user_response =  input() # "No, I don't agrre, I want to mining and exploring in term of disease, drug, side effect of drugs, or symtoms,.. can u revise more data?"
            human_review = await human_preference_agent.run(
                user_prompt=user_response,
                message_history=messages
            )

            review: HumanReview = human_review.output
            if review.is_agreed:
                break
            else:
                messages += human_review.new_messages()


        return SchemaDesignNode(data_dir=self.data_dir, ontology=ontology_result.output)


