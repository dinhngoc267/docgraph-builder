import json


def validate_json_schema(json_schema: str) -> bool:
    try:
        json_object = json.loads(json_schema)
        return True
    except json.JSONDecodeError:
        return False