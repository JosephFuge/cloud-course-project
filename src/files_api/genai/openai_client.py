import os
from typing import Optional

from openai import AsyncOpenAI


def create_openai_client():
    client = AsyncOpenAI()
    return client