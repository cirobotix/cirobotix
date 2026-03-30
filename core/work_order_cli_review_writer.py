from pathlib import Path

from .review import ReviewBuilder
from .context import ProductionContext
from .blueprint import Blueprint
from .profile import ProductionProfile
from .project_context import ProjectContext
from .work_order import WorkOrder


class WorkOrderCliReviewWriter:
    def write(self, work_order: WorkOrder, base_dir: Path) -> None:
        dummy_context = ProductionContext(
            blueprint=Blueprint(
                name=work_order.blueprint_name,
                component_type="review",
                required_fields=[],
            ),
            work_order=work_order,
            profile=ProductionProfile(),
            project=ProjectContext(root_path=Path(".")),
        )

        review_context = ReviewBuilder().run(dummy_context)
        review_path = base_dir / "review.md"
        review_path.write_text(review_context.review_text or "", encoding="utf-8")
