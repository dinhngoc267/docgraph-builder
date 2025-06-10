import asyncio

from pydantic_graph import Graph

import logfire
logfire.configure(token='pylf_v1_us_jRlKtKKS1F5wQn8c9SK4Kvrszj2SJwHCdtCMnJhTwNxB', scrubbing=False)
logfire.instrument_pydantic_ai()


async def main():


    from nodes.ontology_init_node import OntologyInitNode
    from nodes.information_extraction_node import InformationExtractionNode
    from nodes.schema_design_node import SchemaDesignNode

    graph = Graph(nodes=[OntologyInitNode, InformationExtractionNode, SchemaDesignNode])
    result = await graph.run(OntologyInitNode(data_dir="./data/cord-19/articles"))
    print(result)

asyncio.run(main())