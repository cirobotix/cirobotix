from dataclasses import asdict, dataclass, field
from typing import Any

from core.models.work_order_type import WorkOrderType


@dataclass(frozen=True)
class WorkOrder:
    request_id: str
    blueprint_name: str
    profile_name: str
    order_type: WorkOrderType
    goal: str
    payload: dict[str, Any]

    read_files: list[str] = field(default_factory=list)
    writable_files: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["order_type"] = self.order_type.value
        return data
