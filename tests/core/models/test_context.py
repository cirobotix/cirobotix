from pathlib import Path

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.result import StepResult
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType


def test_context_add_error_and_step_result(tmp_path):
    context = ProductionContext(
        blueprint=Blueprint(name="bp", component_type="x", required_fields=[]),
        work_order=WorkOrder(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            order_type=WorkOrderType.CREATE,
            goal="g",
            payload={},
        ),
        profile=ProductionProfile(),
        project=ProjectContext(root_path=tmp_path),
    )

    context.add_error("err")
    context.add_step_result(StepResult(machine_name="M", success=True))

    assert context.errors == ["err"]
    assert context.step_results[0].machine_name == "M"
    assert isinstance(context.written_files, list)
    assert context.base_dir is None
    assert isinstance(Path(tmp_path), Path)
