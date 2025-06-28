import json
import glob

from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_graph import BaseNode, GraphRunContext, End, Graph

from src.models import (
    Dependency,
    BaseDoc,
    RelationshipInstance,
    BaseRelation
)
from src.models.ontology_entity import OntologyEntity
from src._utils import load_extended_models

from neo4j import GraphDatabase
from typing import List, cast


class GraphExporter:
    def __init__(self, driver):
        self.driver = driver  # Neo4j driver instance

    def clear_db(self):
        query = "MATCH (n) DETACH DELETE n"

        with self.driver.session() as session:
            session.run(query)

    def create_node(self, label: str, node_id: str, properties: dict):
        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n += $props
        """
        with self.driver.session() as session:
            result = session.run(query, id=node_id, props=properties)

    def create_relationship(self, type_: str, start_id: str, end_id: str, properties: dict = None):
        query = f"""
        MATCH (a {{id: $start_id}})
        MATCH (b {{id: $end_id}})
        MERGE (a)-[r:{type_}]->(b)
        """
        if properties:
            query += " SET r += $props"

        with self.driver.session() as session:
            result = session.run(query, start_id=start_id, end_id=end_id, props=properties or {})


def export_entity(model: OntologyEntity, exporter: GraphExporter):
    rel_args = []
    if isinstance(model, OntologyEntity):
        model = cast(OntologyEntity, model)
        exporter.create_node(
            model.node_label(),
            model.id,
            # properties=model.model_dump()
            properties={
                k: getattr(model, k)
                for k in model.__pydantic_fields__
                if not isinstance(getattr(model, k), OntologyEntity)
                   and not isinstance(getattr(model, k), BaseRelation)
                   and not (
                        isinstance(getattr(model, k), list)
                        and all(isinstance(i, BaseRelation) for i in getattr(model, k) if i is not None)
                    )
                   and not (
                        isinstance(getattr(model, k), list)
                        and all(isinstance(i, OntologyEntity) for i in getattr(model, k) if i is not None)
                )
            }
        )

    if hasattr(model, "get_relationships"):
        for rel in model.get_relationships():
            rel = cast(RelationshipInstance, rel)
            rel_args.append(
                {
                    "type_": rel.type_,
                    "start_id": rel.subject_id,
                    "end_id": rel.object_id,
                    "properties": rel.properties
                }
            )

    for attr_name, field in model.__pydantic_fields__.items():
        value = getattr(model, attr_name)
        if isinstance(value, OntologyEntity):
            export_entity(value, exporter)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, OntologyEntity):
                    export_entity(item, exporter)

    for rel in rel_args:
        exporter.create_relationship(**rel)

@dataclass
class Neo4jExportNode(BaseNode[None, Dependency, None]):
    list_roots: List[OntologyEntity]
    graph_exporter: GraphExporter = GraphExporter(
        driver=GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))
    )
    async def run(self, ctx: GraphRunContext) -> End:
        self.graph_exporter.clear_db()
        for root in self.list_roots:
            export_entity(root, self.graph_exporter)

        return End(None)


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
#             doc: BaseDoc = ExtendedDoc(**data)
#             list_docs.append(doc)
#
#     graph = Graph(nodes=[Neo4jExportNode])
#     result = await graph.run(Neo4jExportNode(list_docs),
#                              deps=Dependency())
#     print(result)
# import asyncio
# asyncio.run(main())
