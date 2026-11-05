"""Simple LLM client supporting OpenAI, Gemini, and Ollama."""

import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

from openai import OpenAI
from google import genai
from ollama import Client as OllamaClient
from anthropic import Anthropic
from groq import Groq

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_qwq import ChatQwen
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from langchain_groq import ChatGroq

# Load .env from project root (works regardless of cwd)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Read configuration from .env file
PROVIDER = os.getenv("PROVIDER", "openai").lower()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
# Intl (Singapore) endpoint by default; China mainland: https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_BASE_URL = os.getenv(
    "QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

Message = Dict[str, str]

def _call_openai(messages: List[Message]) -> str:
    """Call OpenAI API."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=MODEL, messages=messages
    )

    return response.choices[0].message.content

def _call_gemini(messages: List[Message]) -> str:
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set in the .env file")

    client = genai.Client(api_key=GOOGLE_API_KEY)

    system_text = ""
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        elif msg["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

    config = genai.types.GenerateContentConfig(
        temperature=0,
        system_instruction=system_text if system_text else None,
    )
    response = client.models.generate_content(
        model=MODEL, contents=contents, config=config
    )
    return response.text

def _call_anthropic(messages: List[Message]) -> str:
    """Call Anthropic Claude API."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set in .env")

    system_text = next(
        (msg["content"] for msg in messages if msg["role"] == "system"),
        None
    )

    anthro_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages
        if msg["role"] in ("user", "assistant")
    ]

    if not anthro_messages:
        raise ValueError("Anthropic requires at least one user or assistant message")

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=anthro_messages,
        system=system_text
    )

    return response.content[0].text

def _call_groq(messages: List[Message]) -> str:
    """Call Groq API."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in .env")

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=MODEL, messages=messages
    )

    return response.choices[0].message.content

def _call_qwen(messages: List[Message]) -> str:
    """Call Qwen API."""
    if not QWEN_API_KEY:
        raise ValueError("QWEN_API_KEY not set in .env")

    # Qwen exposes an OpenAI-compatible endpoint; no dashscope SDK needed.
    client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
    response = client.chat.completions.create(
        model=MODEL, messages=messages
    )

    return response.choices[0].message.content

def chat(messages: List[Message]) -> str:
    if not messages:
        raise ValueError("messages cannot be empty")

    if PROVIDER == "openai":
        return _call_openai(messages)

    if PROVIDER == "google":
        return _call_gemini(messages)

    if PROVIDER == "anthropic":
        return _call_anthropic(messages)

    if PROVIDER == "groq":
        return _call_groq(messages)

    if PROVIDER == "qwen":
        return _call_qwen(messages)

    raise NotImplementedError(f"Provider '{PROVIDER}' not supported yet")

def get_langchain_llm():
    if PROVIDER == "openai":
        return ChatOpenAI(model=MODEL, api_key=OPENAI_API_KEY)
    elif PROVIDER == "google":
        return ChatGoogleGenerativeAI(model=MODEL, api_key=GOOGLE_API_KEY)
    elif PROVIDER == "qwen":
        return ChatQwen(model=MODEL, api_key=QWEN_API_KEY,api_base=QWEN_BASE_URL)
    elif PROVIDER == "anthropic":
        return ChatAnthropic(model=MODEL, api_key=ANTHROPIC_API_KEY)
    elif PROVIDER == "groq":
        return ChatGroq(model=MODEL, api_key=GROQ_API_KEY)
    else:
        raise NotImplementedError(f"Provider '{PROVIDER}' not supported yet")