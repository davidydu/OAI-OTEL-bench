import os
from openai import AsyncOpenAI

SGLANG_BASE_URL = os.getenv("SGLANG_BASE_URL")
SGLANG_API_KEY = os.getenv("SGLANG_API_KEY")
SGLANG_MODEL = os.getenv("SGLANG_MODEL", "qwen")

if not SGLANG_BASE_URL:
    raise RuntimeError("SGLANG_BASE_URL environment variable not set")

client = AsyncOpenAI(base_url=SGLANG_BASE_URL, api_key=SGLANG_API_KEY)