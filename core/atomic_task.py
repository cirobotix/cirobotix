from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AtomicTask:
    task_id: str
    blueprint_name: str
    title: str
    description: str
    inputs: dict[str, Any] = field(default_factory=dict)
    acceptance_criteria: list[str] = field(default_factory=list)
