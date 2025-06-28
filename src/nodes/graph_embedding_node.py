import os
from dataclasses import dataclass
from openai import OpenAI
from pydantic_graph import BaseNode, GraphRunContext, End
from dotenv import load_dotenv

from src.models.ontology_entity import OntologyEntity
from src.nodes.neo4j_export_node import Neo4jExportNode

from typing import List

load_dotenv()

def embedding(text: str) -> List[float]:
    """
    Given a text string, use the provided OpenAI client to get an embedding.
    """

    client = OpenAI(
        api_key=os.getenv("MY_API_KEY")
    )
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        encoding_format="float",
    )

    return (
        response.data[0].embedding
        if hasattr(response, "data")
        else response["data"][0]["embedding"]
    )


def recursive_embed_entity(entity: OntologyEntity, embed_func):
    embed_func(entity)
    # entity.embedding = embedding(entity.summary)
    for field_name, value in entity.__dict__.items():
        if isinstance(value, OntologyEntity):
            recursive_embed_entity(value, embed_func)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, OntologyEntity):
                    recursive_embed_entity(item, embed_func)

@dataclass
class GraphEmbeddingNode(BaseNode):
    list_roots: List[OntologyEntity]

    @staticmethod
    def embed_entity(entity: OntologyEntity):
        entity.embedding = embedding(entity.summary)
        return entity

    async def run(self, ctx: GraphRunContext) -> Neo4jExportNode:

        for entity in self.list_roots:
            recursive_embed_entity(entity, self.embed_entity)

        return Neo4jExportNode(self.list_roots)
