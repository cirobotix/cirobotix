from pathlib import Path
import json


class Writer:
    def write(self, request, prompt: str, review: str) -> Path:
        base = Path(".codegen") / request.request_id
        base.mkdir(parents=True, exist_ok=True)

        task_path = base / "task.json"
        prompt_path = base / "prompt.md"
        review_path = base / "review.md"

        task_path.write_text(
            json.dumps(request.to_dict(), indent=2),
            encoding="utf-8",
        )
        prompt_path.write_text(prompt, encoding="utf-8")
        review_path.write_text(review, encoding="utf-8")

        print(f"Generated request package at: {base}")
        return base
