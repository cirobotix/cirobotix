from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .blueprint import Blueprint
from .profile import ProductionProfile
from .project_context import ProjectContext
from .result import StepResult
from .work_order import WorkOrder


@dataclass
class ProductionContext:
    blueprint: Blueprint
    work_order: WorkOrder
    profile: ProductionProfile
    project: ProjectContext

    base_dir: Optional[Path] = None
    prompt_text: Optional[str] = None
    review_text: Optional[str] = None
    response_path: Optional[Path] = None
    assembled_context: Optional[str] = None

    written_files: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    step_results: list[StepResult] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_step_result(self, result: StepResult) -> None:
        self.step_results.append(result)
