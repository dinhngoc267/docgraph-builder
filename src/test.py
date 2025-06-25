from src._utils import load_extended_models
import json
from pydantic import BaseModel

with open("/home/ju/PycharmProjects/automated-docgraph-construction/src/models/extended_doc_schema.json", encoding="utf-8") as f:
    loaded = json.load(f)

code = loaded["schema_code"]
ExtendedDocUnit, ExtendedDoc = load_extended_models(code)

with open("/home/ju/PycharmProjects/automated-docgraph-construction/data/processed/0hlj6r10.txt.json", encoding="utf-8") as f:
    raw_data = json.load(f)

data: BaseModel = ExtendedDoc(**raw_data)

print(data.model_dump())