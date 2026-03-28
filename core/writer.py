import json
from pathlib import Path

from .context import ProductionContext


class Writer:
    def run(self, context: ProductionContext) -> ProductionContext:
        if context.prompt_text is None:
            raise ValueError("prompt_text is missing in ProductionContext")

        if context.review_text is None:
            raise ValueError("review_text is missing in ProductionContext")

        base = Path(".codegen") / "requests" / context.work_order.request_id
        base.mkdir(parents=True, exist_ok=True)

        task_path = base / "task.json"
        prompt_path = base / "prompt.md"
        review_path = base / "review.md"

        task_path.write_text(
            json.dumps(context.work_order.to_dict(), indent=2),
            encoding="utf-8",
        )
        prompt_path.write_text(context.prompt_text, encoding="utf-8")
        review_path.write_text(context.review_text, encoding="utf-8")

        context.base_dir = base

        print(f"Generated request package at: {base}")
        return context
