import json
from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext, End

from src.models import HumanReview

from src.agents import (
    create_doc_distiller_agent,
    create_mention_detection_agent,
    create_relation_extraction_agent
)
import logging

# Logs to terminal by default
logging.basicConfig(
    level=logging.INFO,  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='[%(levelname)s] %(message)s'
)

from src.models import AgentName, create_model_from_schema, build_dynamic_relation_model

from src._utils import task_group_gather


# @dataclass(init=False)
class InformationExtractionNode(BaseNode):

    def __init__(self, data_dir: str, **kwargs):
        super().__init__(**kwargs)

        self.data_dir = data_dir
        schema = json.loads(
            """
                    {
              "$defs": {
                "EntityType": {
                  "type": "string",
                  "enum": [
                    "DRUG",
                    "GENE",
                    "DISEASE",
                    "PERSON",
                    "DATE",
                    "SYMPTOM"
                  ],
                  "description": "The type of the entity."
                },
                "RelationType": {
                  "type": "string",
                  "enum": [
                    "CAUSES",
                    "TREATS",
                    "ASSOCIATED_WITH",
                    "OCCURS_IN",
                    "FOUND_IN",
                    "LINKED_TO",
                    "RELATED_TO"
                  ],
                  "description": "The type of the relationship."
                },
                "Mention": {
                  "type": "object",
                  "properties": {
                    "type_": {
                      "$ref": "#/$defs/EntityType",
                      "description": "The type of the entity mention in the text."
                    },
                    "text": {
                      "type": "string",
                      "description": "The surface form of the entity mention in the text."
                    }
                  },
                  "required": ["_type", "text"]
                },
                "DocUnit": {
                  "type": "object",
                  "properties": {
                    "text": {
                      "type": "string",
                      "description": "The raw text content of this document unit."
                    },
                    "section_title": {
                      "anyOf": [{ "type": "string" }, { "type": "null" }],
                      "description": "The title of the section or unit if present.",
                      "default": null
                    },
                    "unit_id": {
                      "anyOf": [{ "type": "string" }, { "type": "null" }],
                      "description": "A unique identifier for this unit within the document.",
                      "default": null
                    },
                    "mentions": {
                      "anyOf": [
                        {
                          "type": "array",
                          "items": { "$ref": "#/$defs/Mention" }
                        },
                        { "type": "null" }
                      ],
                      "description": "A list of entity mentions found in this unit.",
                      "default": null
                    },
                    "relationships": {
                      "anyOf": [
                        {
                          "type": "array",
                          "items": { "type": "object" }
                        },
                        { "type": "null" }
                      ],
                      "description": "A list of relationships between mentions in this unit.",
                      "default": null
                    }
                  },
                  "required": ["text", "section_title"]
                },
                "Table": {
                  "type": "object",
                  "properties": {
                    "headers": {
                      "type": "array",
                      "items": { "type": "string" },
                      "description": "List of column headers."
                    },
                    "rows": {
                      "type": "array",
                      "items": {
                        "type": "array",
                        "items": { "type": "string" }
                      },
                      "description": "List of rows in the table."
                    },
                    "caption": {
                      "anyOf": [{ "type": "string" }, { "type": "null" }],
                      "description": "Caption or description of the table.",
                      "default": null
                    }
                  },
                  "required": ["headers", "rows"]
                },
                "Figure": {
                  "type": "object",
                  "properties": {
                    "caption": {
                      "anyOf": [{ "type": "string" }, { "type": "null" }],
                      "description": "Caption or description of the figure.",
                      "default": null
                    },
                    "description": {
                      "anyOf": [{ "type": "string" }, { "type": "null" }],
                      "description": "Additional description of the figure.",
                      "default": null
                    },
                    "source": {
                      "anyOf": [{ "type": "string" }, { "type": "null" }],
                      "description": "Source or origin of the figure.",
                      "default": null
                    }
                  },
                  "required": []
                }
              },
              "type": "object",
              "title": "Doc",
              "properties": {
                "title": {
                  "type": "string",
                  "description": "The title of the document."
                },
                "authors": {
                  "type": "array",
                  "items": { "type": "string" },
                  "description": "A list of authors or contributors to the document."
                },
                "abstract": {
                  "anyOf": [{ "type": "string" }, { "type": "null" }],
                  "description": "A brief summary of the document's content.",
                  "default": null
                },
                "units": {
                  "type": "array",
                  "items": { "$ref": "#/$defs/DocUnit" },
                  "description": "A list of segmented content units (e.g., paragraphs, sections)."
                },
                "tables": {
                  "anyOf": [
                    {
                      "type": "array",
                      "items": { "$ref": "#/$defs/Table" }
                    },
                    { "type": "null" }
                  ],
                  "description": "A list of tables included in the document.",
                  "default": null
                },
                "figures": {
                  "anyOf": [
                    {
                      "type": "array",
                      "items": { "$ref": "#/$defs/Figure" }
                    },
                    { "type": "null" }
                  ],
                  "description": "A list of figures included in the document.",
                  "default": null
                },
                "source": {
                  "anyOf": [{ "type": "string" }, { "type": "null" }],
                  "description": "The source or origin of the document.",
                  "default": null
                },
                "doc_type": {
                  "anyOf": [{ "type": "string" }, { "type": "null" }],
                  "description": "The type or category of the document (e.g., research paper, review, case study).",
                  "default": null
                }
              },
              "required": ["title", "authors", "units"]
            }
                    """
        )

        self.relation_types = create_model_from_schema(schema, "RelationType")

        self.doc_model = create_model_from_schema(schema, "Doc")
        logging.info(json.dumps(self.doc_model.model_json_schema(), indent=2))

        self.mention_model = create_model_from_schema(schema, "Mention")
        logging.info(json.dumps(self.mention_model.model_json_schema(), indent=2))

        self.doc_distiller_agent = create_doc_distiller_agent(output_model=self.doc_model, schema="")
        self.mention_detection_agent = create_mention_detection_agent(self.mention_model)

    async def run(self, ctx: GraphRunContext) -> End:

        with open("./data/cord-19/articles/zq387qo8.txt",
                  "r") as f:
            sample_data = f.read()

        doc_result = await self.doc_distiller_agent.run(
            user_prompt=f"Raw document: {sample_data}\n"
        )
        doc_units = doc_result.output.units

        mentions_result = await task_group_gather(
            [
                lambda i=i: self.mention_detection_agent.run(doc_units[i].text)
                for i in range(len(doc_units))
            ]
        )

        for i in range(len(doc_units)):
            doc_units[i].mentions = mentions_result[i].output

        # mentions_result =  await self.mention_detection_agent.run(str(doc_units[0].text))
        # mentions = mentions_result.output

        relation_extraction_agents = []
        for item in mentions_result:
            relation_model = build_dynamic_relation_model(mention_strings=[mention.text for mention in item],
                                                          relation_types=self.relation_types)
            relation_extraction_agents.append(create_relation_extraction_agent(relation_model))

        relations_result = await task_group_gather(
            [
                lambda i=i: relation_extraction_agents[i].run(doc_units[i].text)
                for i in range(len(doc_units))
            ]
        )

        for i in range(len(doc_units)):
            doc_units[i].relations = relations_result[i].output

        return End(doc_units)
