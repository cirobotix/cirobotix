from pathlib import Path

from core.models.context import ProductionContext


class Executor:
    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "The 'openai' package is required to run Executor. "
                "Install project dependencies before executing this step."
            ) from exc
        self.client = OpenAI()

    def run(self, context: ProductionContext) -> ProductionContext:
        base = Path(".codegen") / "requests" / context.work_order.request_id
        prompt_path = base / "prompt.md"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        prompt = prompt_path.read_text(encoding="utf-8")

        response = self.client.responses.create(
            model=context.profile.llm_model,
            input=prompt,
        )

        output_text = getattr(response, "output_text", None)
        if not output_text:
            output_text = str(response)

        output_path = base / "response.md"
        output_path.write_text(output_text, encoding="utf-8")

        context.response_path = output_path
        return context
