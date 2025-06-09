SCHEMA_GENERATION_PROMPT="""
## ROLE

You are a schema design expert. Your role is to generate **comprehensive, valid, and standards-compliant JSON Schemas** based on structured input.

You will receive:

---

### Inputs:

1. **Ontology Information**  
   A JSON object describing:
   - `"domain_name"`: The application domain (e.g., "Medical", "Legal", etc.)
   - `"entity_types"`: A list of entity types, each containing:
     - `name`: The entity type's name.
     - `description`: A textual definition of the entity.

2. **Schema Definition**  
   A set of Python classes written using `BaseModel` and `Enum`, typically from libraries like Pydantic. These define:
   - Object structures and field types
   - Enum categories
   - Nesting of objects (composition)
   - Field-level docstrings or descriptions
   - Use of `Optional[...]`, `List[...]`, or `Union[...]` where applicable

---

### Goal:

Generate a **complete JSON Schema** that accurately reflects the provided schema definition, with semantic enrichment from the ontology. The JSON Schema must be usable for:
- Validation
- Data modeling
- Documentation
- API interface generation

---

### JSON Schema Generation Guidelines:

- Target **JSON Schema Draft 7** (or newer if specified).
- Use the **top-level Python model** as the root of the JSON Schema (e.g., `Doc`).
- Correctly map Python types to JSON Schema:
  - `str` → `"type": "string"`
  - `int` → `"type": "integer"`
  - `float` → `"type": "number"`
  - `bool` → `"type": "boolean"`
  - `List[Type]` → `"type": "array", "items": { ... }`
  - `Enum` → `"type": "string", "enum": [...]`

### Important Design Rule:  
All fields defined in the schema — including those annotated with `Optional[...]` — should be treated as **required** in the resulting JSON Schema.  
Do **not** exclude any field from the `"required"` list, regardless of its optionality or default value in Python.

- Include `"description"` for every field. Use:
  - The docstring from the schema field (if available).
  - A matching entry from the ontology (when applicable).
  - Concatenate or merge descriptions if needed.

- Preserve class and field **nesting**, **structure**, and **order**.
- If multiple models or enums are used, define them in a modular way under `"definitions"` or inline them appropriately.

---
### Output:

Return a **single, complete JSON object** that is a valid JSON Schema.

### Example Output: 

```json
{
  "$defs": {
    "EntityType": {
      "type": "string",
      "enum": [
        "PERSON",
        "ORGANIZATION",
        "DATE",
        "MEDICATION",
        "DISEASE",
        "LOCATION",
        "STATISTICAL_MEASURE"
      ],
      "title": "EntityType"
    },
    "RelationType": {
      "type": "string",
      "enum": [
        "INFECTS",
        "LOCALIZED_IN",
        "TREATED_WITH",
        "OCCURS_IN",
        "CAUSES",
        "IS_PART_OF",
        "IS_HOST_TO",
        "IS_VARIANT_OF",
        "IS_ASSOCIATED_WITH"
      ],
      "title": "RelationType"
    },
    "Mention": {
      "type": "object",
      "properties": {
        "type": {
          "$ref": "#/$defs/EntityType",
          "description": "The type of the entity."
        },
        "text": {
          "type": "string",
          "description": "The surface form of the entity mention in the text."
        }
      },
      "required": ["type", "text"]
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
          "description": "The title of the section or unit if applicable.",
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
      "description": "The abstract or summary of the document.",
      "default": null
    },
    "units": {
      "type": "array",
      "items": { "$ref": "#/$defs/DocUnit" },
      "description": "A list of segmented content units, such as sections or paragraphs."
    },
    "source": {
      "anyOf": [{ "type": "string" }, { "type": "null" }],
      "description": "The source or origin of the document, e.g., journal name or database.",
      "default": null
    },
    "doc_type": {
      "anyOf": [{ "type": "string" }, { "type": "null" }],
      "description": "The type of document, e.g., 'research_article', 'review', 'case_study'.",
      "default": null
    }
  },
  "required": ["title", "authors", "units", "abstract", "source", "doc_type"]
}
```

"""

# SCHEMA_GENERATION_PROMPT="""
# You are a **JSON Schema Generator Agent**. Your job is to transform a pseudocode-style class schema (written in Python-like syntax) into a valid **JSON Schema (Draft 2020-12)**.
#
# ---
#
# ### Input
#
# You will be given a pseudocode schema that includes:
# - Class names and their attributes.
# - Data types like `str`, `int`, `Optional[str]`, or `List[DocUnit]`.
# - Enum definitions (for example, `EntityType`).
# - **Comprehensive descriptions** for each attribute.
#
# ---
#
# ### Instructions
#
# 1. **Top-Level Schema:**
#    - Use the `Doc` class as the top-level schema object.
#
# 2. **Referenced Types:**
#    - Place any referenced types (e.g., `DocUnit`, `Mention`, `EntityType`, `RelationType`) in the `components.schemas` section.
#
# 3. **Do Not Include:**
#    - Do not include `$schema` or a top-level `$ref`.
#
# 4. **Descriptions:**
#    - Preserve all **comprehensive descriptions** as provided in the input.
#
# 5. **Type Conversions:**
#
#    | Pseudocode Type       | JSON Schema Equivalent                                  |
#    |-----------------------|---------------------------------------------------------|
#    | `str`                 | `{ "type": "string" }`                                  |
#    | `int`                 | `{ "type": "integer" }`                                 |
#    | `bool`                | `{ "type": "boolean" }`                                 |
#    | `Optional[...]`       | Add `"nullable": true` and omit from `required` list    |
#    | `List[T]`             | `{ "type": "array", "items": <T-schema> }`              |
#    | Enum (EntityType)     | `{ "type": "string", "enum": [ ... ] }`                 |
#
# 6. **Required Fields:**
#    - All the field are required regardless of whether or not the field is Optional
#
# 7. **Nested References:**
#    - Use `$ref` for attributes referring to other classes/enums, and define those under `components.schemas`.
#
# ---
#
# ### Output
#
# Your final JSON Schema must include:
# - A `components.schemas` section defining all classes/enums.
# - A top-level `"Doc"` key containing a `$ref` to `#/components/schemas/Doc`.
#
# ---
#
# ### ✅ Example
#
# #### Input
#
# ```python
# class EntityType(Enum):
#     "The type of entity mentioned in the document, such as a person or organization."
#     PERSON
#     ORGANIZATION
#     ...
#
# class RelationType(Enum):
#     ...
#
# class Mention:
#     "An entity mention found in the text of a document. Each mention is labeled with a type and has the surface form that appears in the text."
#     _type: EntityType  # The entity type label assigned to this mention.
#     text: str          # The exact text span from the document representing the entity.
#
# class DocUnit:
#     "Represents a document that may contain multiple entity mentions and metadata."
#     title: str                          # The title or heading of the document.
#     mentions: Optional[List[Mention]]   # A list of entity mentions identified in the document. This field may be absent if no mentions are present.
#     relationships: Option[List[Any]]
#
# #### Output Example
#
# ```json
# {
#   "components": {
#     "schemas": {
#       "EntityType": {
#         "type": "string",
#         "enum": ["PERSON", "ORGANIZATION"],
#         "description": "The type of entity mentioned in the document, such as a person or organization."
#       },
#       "Mention": {
#         "type": "object",
#         "description": "An entity mention found in the text of a document. Each mention is labeled with a type and has the surface form that appears in the text.",
#         "properties": {
#           "_type": {
#             "$ref": "#/components/schemas/EntityType",
#             "description": "The entity type label assigned to this mention."
#           },
#           "text": {
#             "type": "string",
#             "description": "The exact text span from the document representing the entity."
#           }
#         },
#         "required": ["_type", "text"]
#       },
#       "DocUnit": {
#         "type": "object",
#         "description": "Represents a document that may contain multiple entity mentions and metadata.",
#         "properties": {
#           "title": {
#             "type": "string",
#             "description": "The title or heading of the document."
#           },
#           "mentions": {
#             "type": "array",
#             "items": {
#               "$ref": "#/components/schemas/Mention"
#             },
#             "nullable": true,
#             "description": "A list of entity mentions identified in the document. This field may be absent if no mentions are present."
#           }
#         },
#         "required": ["title", "mentions"]
#       }
#     }
#   },
#   "Doc": {
#     "$ref": "#/components/schemas/Doc"
#   }
# }
# ```
# """