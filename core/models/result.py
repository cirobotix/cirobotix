from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepResult:
    machine_name: str
    success: bool
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
