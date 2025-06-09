from typing import List, Type
from pydantic import BaseModel, Field, create_model
from typing_extensions import Literal

from pydantic import BaseModel, Field, create_model
from typing import List, Any, Dict, Optional
from enum import Enum

def build_dynamic_relation_model(mention_strings: List[str],
                                 relation_types: Any) -> Type[BaseModel]:

    mention_literals = Literal[tuple(mention_strings)]

    DynamicRelation = create_model(
        "DynamicRelation",
        head=(mention_literals, Field(..., description="The mentioned entity (head) must match upper/lower case.")),
        tail=(mention_literals, Field(..., description="The mentioned entity (tail) must match upper/lower case.")),
        relation_type=(relation_types, Field(..., description="A brief description of the relationship between head and tail entities.")),
    )

    return DynamicRelation


from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, create_model
from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, create_model
import json

from pydantic import BaseModel, create_model, Field
from typing import Any, Dict, List, Optional, Union, Literal

def create_model_from_schema(schema: Dict[str, Any], model_name: str) -> BaseModel:
    """
    Create a Pydantic model from a JSON Schema definition.
    """
    sub_models_cache = {}

    def resolve_ref(ref: str) -> Dict[str, Any]:
        parts = ref.strip("#/").split("/")
        result = schema
        for part in parts:
            result = result[part]
        return result

    def parse_enum_type(name: str, enum_values: List[str]):
        return Literal[tuple(enum_values)]

    def create_sub_model(sub_schema: Dict[str, Any], name: str):
        if name in sub_models_cache:
            return sub_models_cache[name]

        # If it's an enum definition (like EntityType or RelationType)
        if sub_schema.get("type") == "string" and "enum" in sub_schema:
            enum_type = parse_enum_type(name, sub_schema["enum"])
            sub_models_cache[name] = enum_type
            return enum_type

        props = sub_schema.get("properties", {})
        required = sub_schema.get("required", [])
        fields = {}

        for prop, spec in props.items():
            field_type = Any
            default = ... if prop in required else None

            if "$ref" in spec:
                ref_schema = resolve_ref(spec["$ref"])
                ref_name = spec["$ref"].split("/")[-1]
                field_type = create_sub_model(ref_schema, ref_name)

            elif spec.get("type") == "string":
                field_type = str
            elif spec.get("type") == "array":
                item_spec = spec["items"]
                if "$ref" in item_spec:
                    ref_schema = resolve_ref(item_spec["$ref"])
                    ref_name = item_spec["$ref"].split("/")[-1]
                    item_type = create_sub_model(ref_schema, ref_name)
                else:
                    item_type = str
                field_type = List[item_type]
            elif spec.get("type") == "object":
                field_type = dict
            elif spec.get("anyOf"):
                # Handle anyOf with union types
                union_types = []
                for t in spec["anyOf"]:
                    if "$ref" in t:
                        ref_schema = resolve_ref(t["$ref"])
                        ref_name = t["$ref"].split("/")[-1]
                        union_types.append(create_sub_model(ref_schema, ref_name))
                    elif t.get("type") == "string":
                        union_types.append(str)
                    elif t.get("type") == "array":
                        union_types.append(list)
                    elif t.get("type") == "null":
                        union_types.append(type(None))
                field_type = Union[tuple(union_types)]

            if "enum" in spec:
                field_type = parse_enum_type(prop, spec["enum"])

            fields[prop] = (field_type, Field(default, description=spec.get("description", "")))

        model = create_model(name, **fields)
        sub_models_cache[name] = model
        return model

    # Start from either top-level or from $defs
    if model_name in schema.get("$defs", {}):
        top_schema = schema["$defs"][model_name]
    else:
        top_schema = schema
    return create_sub_model(top_schema, model_name)

