from pathlib import Path
from openai import OpenAI


class Executor:
    def __init__(self) -> None:
        self.client = OpenAI()

    def run(self, request_id: str, model: str = "gpt-4o-mini") -> Path:
        base = Path(".codegen") / "requests" / request_id
        prompt_path = base / "prompt.md"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        prompt = prompt_path.read_text(encoding="utf-8")

        response = self.client.responses.create(
            model=model,
            input=prompt,
        )

        output_text = getattr(response, "output_text", None)
        if not output_text:
            output_text = str(response)

        output_path = base / "response.md"
        output_path.write_text(output_text, encoding="utf-8")

        return output_path
