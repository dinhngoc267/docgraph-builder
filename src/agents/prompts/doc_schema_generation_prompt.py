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

Return a **single, complete JSON object** that is a valid JSON Schema. Do not add any explanation. 


### Example Output: 

```json{
  "$defs": {
    "DocUnit": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "section_title": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
        "mentions": {
          "anyOf": [
            { "type": "array", "items":  { "type": "object" } },
            { "type": "null" }
          ],
          "default": null
        },
        "relationships": {
          "anyOf": [
            { "type": "array", "items": { "type": "object" } }, // You could define a Relation object here!
            { "type": "null" }
          ],
          "default": null
        }
      },
      "required": ["text", "section_title"]
    }
  },
  "type": "object",
  "title": "Doc",
  "properties": {
    "title": { "type": "string" },
    "authors": { "type": "array", "items": { "type": "string" } },
    "abstract": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
    "units": { "type": "array", "items": { "$ref": "#/$defs/DocUnit" } },
    "source": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null },
    "doc_type": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null }
  },
  "required": ["title", "authors", "units", "abstract", "source", "doc_type"]

}
```

"""
