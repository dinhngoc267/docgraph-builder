from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext, End

from src.models import HumanReview, Dependency
from rich.prompt import Prompt
from src.agents import (
    create_domain_ontology_agent,
    create_interface_agent,
    create_human_preference_agent,
)

from src.agents.tools import (
    select_sample_data,
    retrieve_data
)

from src.nodes.doc_schema_init_node import DocSchemaDesignNode

ontology_init_agent = create_domain_ontology_agent()
interface_agent = create_interface_agent()
human_preference_agent = create_human_preference_agent()


@dataclass
class OntologyInitNode(BaseNode):
    data_dir: str

    async def run(self, ctx: GraphRunContext) -> DocSchemaDesignNode:

        messages = []
        deps = Dependency(data_dir=self.data_dir)
        sample_data = select_sample_data(data_dir=self.data_dir)

        background = Prompt.ask(
            "Could you tell me more about the data?\n"
            "What is it used for, and what are you planning to use it for?\n"
            "I'm asking to better understand the intention and purpose behind the data, so we can design a more suitable ontology for the knowledge graph.\n"
        )

        while True:
            ontology_result = await ontology_init_agent.run(
                user_prompt=f""" 
                **Background**: {background}
                **Sample data**: {sample_data}
                """ if len(messages)==0  else None,
                message_history=messages,
                deps=deps,
            )

            messages += ontology_result.new_messages()

            interface_response = await interface_agent.run(f"""{str(ontology_result.output)}""")
            messages += interface_response.new_messages()

            user_response = Prompt.ask(interface_response.output)
            human_review = await human_preference_agent.run(
                user_prompt=user_response,
                message_history=messages
            )

            review: HumanReview = human_review.output
            if review.is_agreed:
                break
            else:
                messages += human_review.new_messages()


        return DocSchemaDesignNode(data_dir=self.data_dir,
                                   domain_ontology=ontology_result.output,
                                   schema_output_path="/home/ju/PycharmProjects/automated-docgraph-construction/src/models/extended_doc_schema.json")

#         print("""Could you tell me more about the data?
# What is it used for, and what are you planning to use it for?
#
# I'm asking to better understand the intention and purpose behind the data, so we can design a more suitable ontology for the knowledge graph.
#         """)
#
#         background = """
# The data is the CORD-19 dataset, which is a large collection of scientific articles related to COVID-19 and coronaviruses. It contains full-text papers, metadata, and abstracts.We plan to use this data to extract structured information about biomedical entities focus on drugs, proteins, diseases, and their relationships. The goal is to build a knowledge graph that integrates this information to support downstream tasks such as scientific question answering, drug discovery, and literature-based hypothesis generation.
#         """

# I just want to focus on DRUG, DISEASE, SYMPTOM, VIRUS entity types and TREATS, CAUSES, HAS SIDE EFFECT and HAS SYMPTOM relationship types