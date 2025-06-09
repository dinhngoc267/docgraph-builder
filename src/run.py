import asyncio

from src.agents import (
    create_human_preference_agent,
    create_ontology_init_agent,
    create_interface_agent
)

from pydantic_graph import Graph

import logfire
logfire.configure(token='pylf_v1_us_jRlKtKKS1F5wQn8c9SK4Kvrszj2SJwHCdtCMnJhTwNxB', scrubbing=False)
logfire.instrument_pydantic_ai()

# def scrubbing_callback(match: logfire.ScrubMatch):
#     # `my_safe_value` often contains the string 'password' but it's not actually sensitive.
#     if match.path == ('attributes', 'my_safe_value') and match.pattern_match.group(0) == 'password':
#         # Return the original value to prevent redaction.
#         return match.value
#
# logfire.configure(scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback))
# logfire.configure(scrubbing=False)

async def main():

    import json
    # data = json.load(open("/home/ju/PycharmProjects/docgraph-construction/notebooks/history_textbook.json"))
    #
    # sample = "Title: Những năm đầu của cuộc kháng chiến toàn quốc chống thực dân Pháp (1946 - 1950)"
    #
    # for i,(key, value) in enumerate(data['Lớp 12']['Việt Nam từ năm 1945 đến năm 1954']['Những năm đầu của cuộc kháng chiến toàn quốc chống thực dân Pháp (1946 - 1950)'].items()):
    #     sample += f"\n{str(i)} {key}\n{value}"



    from nodes.ontology_init_node import OntologyInitNode
    from nodes.information_extraction_node import InformationExtractionNode
    from nodes.schema_design_node import SchemaDesignNode

    graph = Graph(nodes=[OntologyInitNode, InformationExtractionNode, SchemaDesignNode])
    graph = Graph(nodes=[ InformationExtractionNode])

    result = await graph.run(InformationExtractionNode(data_dir="./data/cord-19/articles"))
    # await ontology_init_node.run()


    # interface_agent = create_interface_agent()
    # ontology_init_agent = create_ontology_init_agent()
    #

    # result = await ontology_init_agent.run(sample)
    # print(result.new_messages())
    # print(result.output)
    # print("============")
    # result = await interface_agent.run(str(result.output))
    # print(result.output)

asyncio.run(main())