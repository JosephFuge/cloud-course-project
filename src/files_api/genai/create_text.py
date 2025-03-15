"""Create a text file using Generative AI and return it."""

from typing import Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from files_api.genai.openai_client import create_openai_client


async def create_text_file(prompt: str, client: Optional[AsyncOpenAI] = None) -> bytes:
    """Generate and return a new file using the provided prompt."""

    if client is None:
        print("creating openAI client...")
        client = create_openai_client()
    
    print("Getting a chat completion...")
    response: ChatCompletion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
        n=1,
    )

    content = response.choices[0].message.content

    print(f"text file content: {content}")

    if content:
        return bytearray(content, 'utf-8')

    raise ValueError('Unable to create text file.')

