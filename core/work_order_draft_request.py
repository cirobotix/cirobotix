from dataclasses import dataclass
from typing import Optional

from .work_order_type import WorkOrderType


@dataclass(frozen=True)
class WorkOrderDraftRequest:
    request_id: str
    blueprint_name: str
    profile_name: str
    order_type: WorkOrderType

    target_name: str
    target_kind: str
    target_import_path: str
    target_path: str
    test_path: Optional[str] = None
