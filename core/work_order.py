from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class WorkOrder:
    request_id: str
    blueprint_name: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
