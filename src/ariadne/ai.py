import json
from openai import OpenAI
from .config import settings

class AIClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )

    def get_completion(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        response = self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            extra_headers={
                "HTTP-Referer": "https://github.com/IsaiahN/Ariadnes-Mirror",
                "X-Title": "Ariadne's Mirror",
            }
        )
        content = response.choices[0].message.content
        return self._strip_markdown_fences(content)

    def _strip_markdown_fences(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```"):
            # Find the first newline to skip things like ```json
            newline_idx = content.find("\n")
            if newline_idx != -1:
                content = content[newline_idx:].strip()
            else:
                content = content[3:].strip()

            if content.endswith("```"):
                content = content[:-3].strip()
        return content

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=settings.openrouter_embedding_model,
            input=texts
        )
        return [data.embedding for data in response.data]
