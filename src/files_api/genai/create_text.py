"""Create a text file using Generative AI and return it."""

from openai.types.chat import ChatCompletion

from files_api.genai.openai_client import create_openai_client


def create_text_file(prompt: str, api_key: str) -> bytes:
    """Generate and return a new file using the provided prompt."""

    client = create_openai_client(api_key)
    response: ChatCompletion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
        n=1,
    )

    content = response.choices[0].message.content

    if content:
        return bytearray(content, 'utf-8')

    raise ValueError('Unable to create text file.')

