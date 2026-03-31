from pathlib import Path

import yaml

from core.models.atomic_task import AtomicTask


class AtomicTaskLoader:
    def load(self, path: str) -> AtomicTask:
        task_path = Path(path)

        if not task_path.exists():
            raise FileNotFoundError(f"Atomic task file not found: {task_path}")

        data = yaml.safe_load(task_path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError("Atomic task file must contain a YAML mapping.")

        return AtomicTask(
            task_id=data["task_id"],
            blueprint_name=data["blueprint_name"],
            title=data["title"],
            description=data["description"],
            inputs=data.get("inputs", {}),
            acceptance_criteria=data.get("acceptance_criteria", []),
        )
