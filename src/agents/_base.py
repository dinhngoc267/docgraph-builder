from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.config import BASE_URL, MODEL_NAME

ollama_model = OpenAIModel(
    model_name= "qwen3:30b-a3b-q4_K_M-32k", #qwen2.5:72b-instruct-q4_K_M-32k",
    provider=OpenAIProvider(base_url=f"{BASE_URL}/v1")
)
tiny_model = OpenAIModel(
    model_name="qwen3:30b-a3b-q4_K_M-32k", #"qwen2.5:72b-instruct-q4_K_M",
    #model_name="qwen2.5:72b-instruct-q4_K_M-32k",
    provider=OpenAIProvider(base_url=f"{BASE_URL}/v1")
)
coder_model = OpenAIModel(
    model_name= "qwen2.5-coder",
    provider=OpenAIProvider(base_url=f"{BASE_URL}/v1")
)
# LMM_API_BASE=
# LMM_API_KEY=