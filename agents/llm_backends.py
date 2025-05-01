from __future__ import annotations
import os
from smolagents import LiteLLMModel

def get_model():
    if os.getenv("OPENAI_API_KEY"):
        return LiteLLMModel(model_id="gpt-4o")
    raise RuntimeError("No LLM credentials found (OPENAI_API_KEY)")