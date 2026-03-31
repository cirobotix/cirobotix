from pathlib import Path

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.services.review import ReviewBuilder


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
            project=ProjectContext(root_path=Path("..")),
        )

        review_context = ReviewBuilder().run(dummy_context)
        review_path = base_dir / "review.md"
        review_path.write_text(review_context.review_text or "", encoding="utf-8")
