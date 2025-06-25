from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.config import BASE_URL, MODEL_NAME
from dotenv import load_dotenv
load_dotenv()
import os


instruct_model = OpenAIModel(
    model_name= "gpt-4.1-mini",
    provider=OpenAIProvider(api_key=os.getenv("MY_API_KEY"))
)

coder_model = OpenAIModel(
    model_name= "qwen2.5-coder",
    provider=OpenAIProvider(base_url=f"{BASE_URL}/v1")
)
