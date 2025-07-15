from __future__ import annotations


from ..file_router import Attachment
from openai import OpenAI

DEFAULT_PROMPT = "Extract any text from this pdf file and describe all contents in comprehensive detail."


class PDFVisionAgent:
    """Use GPT-4.1 to read PDFs."""

    def __init__(self, prompt: str = DEFAULT_PROMPT) -> None:
        self.prompt = prompt

    def process(self, att: Attachment) -> str:
        client = OpenAI()
        file = client.files.create(
            file=open(att.path, "rb"),
            purpose="user_data"
        )
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": file.id,
                        },
                        {
                            "type": "input_text",
                            "text": self.prompt,
                        }
                    ]
                }
            ]
        )
        return response.output_text
