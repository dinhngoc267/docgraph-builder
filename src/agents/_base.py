from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.config import BASE_URL, MODEL_NAME

instruct_model = OpenAIModel(
    model_name= MODEL_NAME,
    provider=OpenAIProvider(base_url=f"{BASE_URL}/v1")
)
coder_model = OpenAIModel(
    model_name= "qwen2.5-coder",
    provider=OpenAIProvider(base_url=f"{BASE_URL}/v1")
)