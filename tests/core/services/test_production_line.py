import pytest

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.production_line import ProductionLine


class OkMachine:
    def run(self, context):
        context.prompt_text = "ok"
        return context


class FailingMachine:
    def run(self, context):
        raise ValueError("boom")


def _context(tmp_path, fail_on_quality_error):
    return ProductionContext(
        blueprint=Blueprint(name="bp", component_type="x", required_fields=[]),
        work_order=WorkOrder(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            order_type=WorkOrderType.CREATE,
            goal="g",
            payload={},
        ),
        profile=ProductionProfile(fail_on_quality_error=fail_on_quality_error),
        project=ProjectContext(root_path=tmp_path),
    )


def test_production_line_happy_and_non_failfast(tmp_path):
    ctx = _context(tmp_path, False)
    updated = ProductionLine([OkMachine(), FailingMachine()]).run(ctx)

    assert updated.prompt_text == "ok"
    assert len(updated.step_results) == 2
    assert any("FailingMachine" in error for error in updated.errors)


def test_production_line_failfast_raises(tmp_path):
    ctx = _context(tmp_path, True)
    with pytest.raises(ValueError):
        ProductionLine([FailingMachine()]).run(ctx)
