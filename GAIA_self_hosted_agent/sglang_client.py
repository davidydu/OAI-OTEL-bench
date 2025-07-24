"""Configure the OpenAI Agents SDK to talk to a self-hosted SGLang endpoint."""

from __future__ import annotations

import os

from agents import set_default_openai_client, set_default_openai_api
from openai import AsyncOpenAI

SGLANG_BASE_URL = os.getenv("SGLANG_BASE_URL")
"""Base URL of the SGLang server (e.g. ``http://<pod_ip>:8000/v1``)."""

SGLANG_API_KEY = os.getenv("SGLANG_API_KEY", "x")
"""Optional API key if authentication is enabled."""

SGLANG_MODEL = os.getenv("SGLANG_MODEL", "openai/Qwen/Qwen3-8B")
"""Default model name used for agent calls."""

if not SGLANG_BASE_URL:
    raise RuntimeError("SGLANG_BASE_URL environment variable not set")

_client = AsyncOpenAI(base_url=SGLANG_BASE_URL, api_key=SGLANG_API_KEY)
set_default_openai_client(_client, use_for_tracing=False)
set_default_openai_api("chat_completions")
# set_default_openai_api("responses")

__all__ = ["SGLANG_MODEL"]