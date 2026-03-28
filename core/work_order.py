from dataclasses import dataclass, asdict, field
from typing import Any

from .work_order_type import WorkOrderType


@dataclass(frozen=True)
class WorkOrder:
    request_id: str
    blueprint_name: str
    payload: dict[str, Any]
    order_type: WorkOrderType = WorkOrderType.CREATE
    read_files: list[str] = field(default_factory=list)
    writable_files: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
