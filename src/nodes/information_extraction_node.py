import json
from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext, End
from typing import Literal, get_args
from src.models import HumanReview
from src.agents import (
    create_doc_distiller_agent,
    create_mention_detection_agent,
    create_relation_extraction_agent
)
import glob
import os
from tqdm import tqdm

from src.models import AgentName, create_model_from_schema, build_dynamic_relation_model

from src._utils import task_group_gather


# @dataclass(init=False)
class InformationExtractionNode(BaseNode):

    def __init__(self, data_dir: str, schema: dict, **kwargs):
        super().__init__(**kwargs)

        self.data_dir = data_dir

        self.relation_types = create_model_from_schema(schema, "RelationType")
        self.entity_types = create_model_from_schema(schema, "EntityType")

        self.doc_model = create_model_from_schema(schema, "Doc")

        self.mention_model = create_model_from_schema(schema, "Mention")

        self.doc_distiller_agent = create_doc_distiller_agent(output_model=self.doc_model, schema="")
        self.mention_detection_agent = create_mention_detection_agent(self.mention_model,
                                                                      entity_types=list(get_args(self.entity_types)))


    async def run_task(self, data: str, output_path: str):
        doc_result = await task_group_gather(
            [
                lambda: self.doc_distiller_agent.run(
                    user_prompt=f"Raw document: {data}\n"
                )
            ],
            timeout_seconds=1000,
        )
        doc_result = doc_result[0]
        doc = doc_result.output
        doc_units = doc.units

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
        for idx, item in enumerate(mentions_result):
            if len(item.output) > 0:
                relation_model = build_dynamic_relation_model(mention_strings=[mention.text for mention in item.output],
                                                              relation_types=self.relation_types)

                relation_extraction_agents.append(
                    create_relation_extraction_agent(relation_model,
                                                     mention_strings=[mention.text for mention in item.output],
                                                     relation_types=list(get_args(self.relation_types)))
                )

        relations_result = await task_group_gather(
            [
                lambda i=i: relation_extraction_agents[i].run(doc_units[i].text)
                for i in range(len(doc_units))
            ],
            timeout_seconds=180
        )

        for i in range(len(doc_units)):  # (non_empty_indices):
            try:
                doc_units[i].relationships = relations_result[i].output
            except:
                doc_units[i].relationships = None
        doc.units = doc_units

        with open(output_path, "w") as f:
            json.dump(doc.dict(), f, indent=2)


    async def run(self, ctx: GraphRunContext) -> End:

        files = glob.glob(os.path.join(self.data_dir, "*.txt"))

        args = []
        for file in tqdm(files):
            with open(file,"r") as f:
                basename = os.path.basename(file)
                sample_data = f.read()
                output_path = f"data/processed/{basename}.json"

                args.append([sample_data, output_path])

        bs=10
        for i in range(0,len(args),bs):
            _ = await task_group_gather(
                [
                    (lambda sample_data=sample_data, output_path=output_path: self.run_task(data=sample_data,
                                                                                            output_path=output_path))
                    for sample_data, output_path in args[i:i+bs]
                ],
                timeout_seconds=120,
        )

        return End(None)