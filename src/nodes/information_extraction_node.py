import json
import random
from dataclasses import dataclass, Field

from pydantic_graph import BaseNode, GraphRunContext, End
from typing import Literal, get_args, List
from src.models import HumanReview, DomainOntology, BaseDoc, BaseDocUnit
from src.agents import (
    create_doc_distiller_agent,
    create_mention_detection_agent,
    create_relation_extraction_agent
)
import glob
import os
from tqdm import tqdm
from pydantic import create_model, Field

from src.models import (
    AgentName,
    Dependency,
    BaseMention,
    create_model_from_schema,
    build_dynamic_relation_model
)
from src._utils import task_group_gather

from .graph_enhancement_node import GraphEnhancementNode
from itertools import count
#
# class IDGenerator:
#     def __init__(self,start: int = 1):
#         self._counter = count(start)
#
#     def next_id(self, node_label:str) -> str:
#         return f"{node_label}{str(next(self._counter)).zfill(4)}"

# @dataclass(init=False)
class InformationExtractionNode(BaseNode[None, Dependency, None]):

    def __init__(self,
                 data_dir: str,
                 domain_ontology: DomainOntology,
                 doc_schema: BaseDoc,
                 **kwargs):
        super().__init__(**kwargs)

        # self.id_generator = IDGenerator()

        self.domain_ontology = domain_ontology
        self.doc_model = doc_schema

        self.data_dir = data_dir

        self.entity_types = Literal[tuple([item.name for item in self.domain_ontology.entity_types])]
        self.relation_types = Literal[tuple([item.name for item in self.domain_ontology.relationship_types])]

        self.mention_model = create_model(
            "Mention",
            __base__= BaseMention,
            entity_type=self.entity_types,
        )

        self.doc_distiller_agent = create_doc_distiller_agent(output_model=self.doc_model, schema="")
        self.mention_detection_agent = create_mention_detection_agent(self.mention_model,
                                                                      entity_types=list(get_args(self.entity_types)))

    async def run_task(self, ctx: GraphRunContext[None, Dependency], data: str, output_path: str):
        doc_result = await task_group_gather(
            [
                lambda: self.doc_distiller_agent.run(
                    user_prompt=f"Raw document: {data}\n"
                )
            ],
            timeout_seconds=1000,
        )

        doc_result = doc_result[0]
        doc: BaseDoc = doc_result.output
        # doc.id = self.id_generator.next_id(doc.node_label())

        doc_units: List[BaseDocUnit] = doc.units
        # for doc_unit in doc_units:
        #     doc_unit.id = self.id_generator.next_id(doc_unit.node_label())

        mentions_result = await task_group_gather(
            [
                lambda i=i: self.mention_detection_agent.run(
                    user_prompt=f"""Passage: {doc_units[i].text}\n
                                    Entity types: {list(get_args(self.entity_types))}"""
                )
                for i in range(len(doc_units))
            ],
            timeout_seconds=180
        )

        for i in range(len(doc_units)):
            doc_units[i].mentions = mentions_result[i].output

        relation_extraction_agents = []
        relation_indices = []
        for idx, mention_list in enumerate(mentions_result):
            if len(mention_list.output) > 0:
                mention_strings = [
                    str(item) for item in mention_list.output
                ]

                relation_model = build_dynamic_relation_model(mention_strings=mention_strings,
                                                              relation_types=list(get_args(self.relation_types)))

                relation_extraction_agents.append(
                    create_relation_extraction_agent(relation_model,
                                                     constraints=str(self.domain_ontology.relationship_types),
                                                     mention_strings=mention_strings,
                                                     relation_types=list(get_args(self.relation_types)))
                )

                relation_indices.append(idx)

        relations_result = await task_group_gather(
            [
                lambda i=i: relation_extraction_agents[i].run(
                    user_prompt=doc_units[relation_indices[i]].text,
                    deps=self.domain_ontology,
                    model_settings={"parallel_tool_calls": False}
                )
                for i in range(len(relation_extraction_agents))
            ],
            timeout_seconds=180
        )

        for rel_idx, doc_idx in enumerate(relation_indices):
            try:
                doc_units[doc_idx].relationships = relations_result[rel_idx].output
            except:
                doc_units[doc_idx].relationships = None

        doc.units = doc_units

        # with open(output_path, "w") as f:
        #     json.dump(doc.model_dump(), f, indent=2)

        return doc

    async def run(self, ctx: GraphRunContext[None, Dependency]) -> GraphEnhancementNode:

        files = glob.glob("/home/ju/PycharmProjects/automated-docgraph-construction/data/cord-19/articles/*.txt")[:20]

        args = []
        for file in tqdm(files):
            with open(file, "r") as f:
                basename = os.path.basename(file).replace(".txt", "")
                sample_data = f.read()
                output_path = f"data/processed/{basename}.json"

                args.append([sample_data, output_path])

        bs = 10

        list_docs = []
        for i in range(0, len(args), bs):
            result = await task_group_gather(
                [
                    (lambda sample_data=sample_data, output_path=output_path: self.run_task(
                        ctx=ctx,
                        data=sample_data,
                        output_path=output_path))
                    for sample_data, output_path in args[i:i + bs]
                ],
                timeout_seconds=120,
            )
            list_docs.extend(result)


        return GraphEnhancementNode(list_docs=list_docs)
