import os
from typing import Optional

from openai import AsyncOpenAI


def create_openai_client(openai_api_key: str, base_url: Optional[str] = None):
    client = AsyncOpenAI(api_key=openai_api_key, base_url=base_url)
    return client