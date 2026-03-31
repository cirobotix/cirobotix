from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.review import ReviewBuilder


def test_review_builder_happy_path_and_list_formatting(tmp_path):
    context = ProductionContext(
        blueprint=Blueprint(name="bp", component_type="x", required_fields=[]),
        work_order=WorkOrder(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            order_type=WorkOrderType.CREATE,
            goal="g",
            payload={"items": [1, 2], "x": "y"},
            read_files=["a.py"],
            writable_files=["b.py"],
            invariants=["i"],
            acceptance_criteria=["a"],
        ),
        profile=ProductionProfile(),
        project=ProjectContext(root_path=tmp_path),
    )

    updated = ReviewBuilder().run(context)

    assert "# Review Summary" in (updated.review_text or "")
    assert "[1, 2]" in (updated.review_text or "")
    assert ReviewBuilder()._format_value([]) == "[]"
