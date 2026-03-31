from enum import Enum


class WorkOrderType(str, Enum):
    CREATE = "create"
    MODIFY = "modify"
