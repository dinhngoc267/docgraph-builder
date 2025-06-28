import asyncio
from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext, Graph, End

from src.models import (
    BaseMention,
    BaseDoc,
    BaseDocUnit,
    Dependency,
)
from src._utils import load_extended_models
from src.nodes.graph_embedding_node import GraphEmbeddingNode
from typing import cast, List


class LinkingManager:
    def __init__(self):
        self.reference_set = {}
        self.__next_id = 0

    @property
    def next_id(self) -> str:
        self.__next_id += 1
        return str(self.__next_id).zfill(4)

    def link_mention(self, mention: BaseMention):
        if mention.text not in self.reference_set:
            self.reference_set[mention.text] = self.next_id
        mention.id = self.reference_set[mention.text]
        return {mention.text: mention.id}


@dataclass
class GraphEnhancementNode(BaseNode[None, Dependency, None]):
    list_docs: List[BaseDoc]
    linking_manager: LinkingManager = LinkingManager()

    async def run(self, ctx: GraphRunContext) -> GraphEmbeddingNode:

        for doc in self.list_docs:
            for unit in doc.units:
                unit = cast(BaseDocUnit, unit)
                local_mention_reference = {}
                if unit.mentions:
                    for mention in unit.mentions:
                        local_mention_reference.update(self.linking_manager.link_mention(mention))
                if unit.relationships:
                    for relation in unit.relationships:
                        relation.subject = local_mention_reference.get(relation.subject)
                        relation.object = local_mention_reference.get(relation.object)

        return GraphEmbeddingNode(self.list_docs)



#
# async def main():
#
#     import json
#     import glob
#
#     with open("/home/ju/PycharmProjects/automated-docgraph-construction/src/models/extended_doc_schema.json", encoding="utf-8") as f:
#         loaded = json.load(f)
#     code = loaded["schema_code"]
#
#     ExtendedDoc, ExtendedDocUnit = load_extended_models(code)
#     from pydantic import BaseModel
#     list_docs = []
#     files = glob.glob(f"/home/ju/PycharmProjects/automated-docgraph-construction/data/processed/*.json")
#     for file in files:
#         with open(file, encoding="utf-8") as f:
#             data = json.load(f)
#             doc: BaseModel = ExtendedDoc(**data)
#             list_docs.append(doc)
#
#     graph = Graph(nodes=[GraphEnhancementNode])
#     result = await graph.run(GraphEnhancementNode(list_docs),
#                              deps=Dependency())
#     print(result)
#
# asyncio.run(main())