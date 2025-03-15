"""Create an image file using Generative AI and return it."""

from io import BytesIO
from typing import Optional

import requests
from openai import AsyncOpenAI
from openai.types.images_response import ImagesResponse

from files_api.genai.openai_client import create_openai_client


async def create_image_file(prompt: str, client: Optional[AsyncOpenAI] = None) -> bytes:
    """Generate and return a new image file using the provided prompt."""

    if client is None:
        client = create_openai_client()
    
    response: ImagesResponse = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    if image_url:
        return image_url_to_bytes(image_url)

    raise ValueError('Unable to create image file.')


def image_url_to_bytes(url: str) -> bytes:
    """Reads an image from a URL and converts it to bytes.

    Args:
        url: The URL of the image.

    Returns:
        The image as bytes, or None if an error occurred.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        image = BytesIO(response.content)
        image_bytes = image.getbuffer().tobytes()
        return image_bytes
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error downloading image: {e}")
    except Exception as e:
        raise ValueError(f"Error processing image: {e}")