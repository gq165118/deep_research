"""OpenAI-compatible client helpers.

Force all OpenAI/httpx traffic to ignore system proxy settings so local broken
Windows proxy entries do not leak into agent, RAG, and memory requests.
"""

import httpx
from langchain_openai import ChatOpenAI
from openai import OpenAI


def build_sync_http_client(timeout: float = 60.0) -> httpx.Client:
    return httpx.Client(trust_env=False, timeout=timeout)


def build_async_http_client(timeout: float = 60.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(trust_env=False, timeout=timeout)


def build_openai_client(api_key: str, base_url: str, timeout: float = 60.0) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=build_sync_http_client(timeout=timeout),
    )


def build_chat_openai(
    *,
    model: str,
    api_key: str,
    base_url: str,
    temperature: float,
    timeout: float = 60.0,
) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        http_client=build_sync_http_client(timeout=timeout),
        http_async_client=build_async_http_client(timeout=timeout),
    )
