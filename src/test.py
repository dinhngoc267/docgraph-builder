from src._utils import load_extended_models
import json
from pydantic import BaseModel
from src.models import BaseDoc

with open("/home/ju/PycharmProjects/automated-docgraph-construction/src/models/extended_doc_schema.json", encoding="utf-8") as f:
    loaded = json.load(f)

code = loaded["schema_code"]
ExtendedDoc, ExtendedDocUnit  = load_extended_models(code)

with open("/home/ju/PycharmProjects/automated-docgraph-construction/data/processed/av8b8g8c.txt.json", encoding="utf-8") as f:
    raw_data = json.load(f)

data: BaseDoc = ExtendedDoc(**raw_data)

print(data.model_dump())