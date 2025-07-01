from __future__ import annotations

from ..file_router import Attachment
import base64
from openai import OpenAI

DEFAULT_PROMPT = "Extract any text from this image and describe all contents in detail."


class ImageVisionAgent:
    """Use GPT-4.1 to analyze images."""

    def __init__(self, prompt: str = DEFAULT_PROMPT) -> None:
        self.prompt = prompt

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        

    def process(self, att: Attachment) -> str:
        client = OpenAI()
        image_path = att.path
        print(image_path)
        base64_image = self.encode_image(image_path)

        response = client.responses.create(
        model="gpt-4.1",
        input=[
                {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": self.prompt},
                        {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ],
        )
        return response.output_text