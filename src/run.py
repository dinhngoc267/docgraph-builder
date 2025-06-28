import asyncio

from pydantic_graph import Graph
from models import Dependency
import logfire
logfire.configure(token='pylf_v1_us_jRlKtKKS1F5wQn8c9SK4Kvrszj2SJwHCdtCMnJhTwNxB', scrubbing=False)
logfire.instrument_pydantic_ai()

import time
time.sleep(1)

from nodes.domain_ontology_init_node import OntologyInitNode
from nodes.information_extraction_node import InformationExtractionNode
from nodes.doc_schema_init_node import DocSchemaDesignNode
from nodes.graph_enhancement_node import GraphEnhancementNode
from nodes.graph_embedding_node import GraphEmbeddingNode
from nodes.neo4j_export_node import Neo4jExportNode

async def main():
    graph = Graph(nodes=[
        OntologyInitNode,
        DocSchemaDesignNode,
        InformationExtractionNode,
        GraphEnhancementNode,
        GraphEmbeddingNode,
        Neo4jExportNode
    ])

    result = await graph.run(OntologyInitNode(data_dir="./data/cord-19/articles"),
                             deps=Dependency())
    print(result)

asyncio.run(main())