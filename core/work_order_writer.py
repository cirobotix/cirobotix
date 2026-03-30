import json
from pathlib import Path

import yaml

from .work_order import WorkOrder


class WorkOrderWriter:
    def write(self, work_order: WorkOrder, base_dir: Path) -> None:
        base_dir.mkdir(parents=True, exist_ok=True)

        json_path = base_dir / "task.json"
        yaml_path = base_dir / "task.yaml"

        payload = work_order.to_dict()

        json_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        yaml_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
