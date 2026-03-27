from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .blueprint import Blueprint
from .profile import ProductionProfile
from .work_order import WorkOrder


@dataclass
class ProductionContext:
    blueprint: Blueprint
    work_order: WorkOrder
    profile: ProductionProfile

    base_dir: Optional[Path] = None
    prompt_text: Optional[str] = None
    review_text: Optional[str] = None
    response_path: Optional[Path] = None

    written_files: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
