"""Create a text file using Generative AI and return it."""

from typing import Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from files_api.genai.openai_client import create_openai_client


async def create_audio_file(prompt: str, client: Optional[AsyncOpenAI] = None) -> bytes:
    """Generate and return a new file using the provided prompt."""

    if client is None:
        client = create_openai_client()
    
    async with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="echo",
        input="""
        I wanna be the very best
        Like no one ever was
        To catch them is my real test
        To train them is my cause""",
    ) as response:
        await response.stream_to_file("speech.mp3")
        audio_chunks = []
        async for chunk in response.iter_bytes():
            audio_chunks.append(chunk)
        audio_content = bytes().join(audio_chunks)

    if audio_content and len(audio_content) > 0:
        return audio_content

    raise ValueError('Unable to create audio file.')

