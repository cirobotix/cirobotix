from pathlib import Path

import yaml

from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType


class WorkOrderLoader:
    def load(self, path: str) -> WorkOrder:
        work_order_path = Path(path)

        if not work_order_path.exists():
            raise FileNotFoundError(f"Work order file not found: {work_order_path}")

        data = yaml.safe_load(work_order_path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError("Work order file must contain a YAML mapping.")

        return WorkOrder(
            request_id=data["request_id"],
            blueprint_name=data["blueprint_name"],
            profile_name=data["profile_name"],
            order_type=WorkOrderType(data["order_type"]),
            goal=data.get("goal", ""),
            payload=data["payload"],
            read_files=data.get("read_files", []),
            writable_files=data.get("writable_files", []),
            invariants=data.get("invariants", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
        )
