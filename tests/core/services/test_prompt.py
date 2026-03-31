from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.prompt import PromptBuilder


def test_prompt_builder_happy_path_and_test_only_rule(tmp_path):
    blueprint = Blueprint(
        name="bp",
        component_type="unit_test",
        required_fields=[],
        constraints=["c1"],
        quality_requirements=["q1"],
    )
    work_order = WorkOrder(
        request_id="r",
        blueprint_name="bp",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        goal="g",
        payload={"target_path": "core/x.py", "list": ["a", "b"]},
        read_files=["core/x.py"],
        writable_files=["tests/test_x.py"],
        invariants=["inv"],
        acceptance_criteria=["acc"],
    )
    context = ProductionContext(
        blueprint=blueprint,
        work_order=work_order,
        profile=ProductionProfile(),
        project=ProjectContext(root_path=tmp_path, source_roots=["core"], test_roots=["tests"]),
        assembled_context="CTX",
    )

    updated = PromptBuilder().run(context)

    assert "# Output Rules" in (updated.prompt_text or "")
    assert "Test-Only Rule" in (updated.prompt_text or "")
    assert "[a, b]" in (updated.prompt_text or "")
    assert PromptBuilder()._format_value([]) == "[]"
    assert PromptBuilder()._format_value("x") == "x"
