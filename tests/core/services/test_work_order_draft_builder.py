import pytest

from core.models.blueprint import Blueprint
from core.models.context_dependency import ContextDependencyResolution
from core.models.target_analysis import TargetAnalysis
from core.models.work_order_draft_request import WorkOrderDraftRequest
from core.models.work_order_type import WorkOrderType
from core.services.work_order_draft_builder import WorkOrderDraftBuilder


def test_build_python_unit_test_draft_happy_path():
    builder = WorkOrderDraftBuilder()
    request = WorkOrderDraftRequest(
        request_id="r",
        blueprint_name="python_pytest_unit_test",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        target_name="X",
        target_kind="class",
        target_import_path="core.x",
        target_path="core/x.py",
        test_path="tests/core/test_x.py",
    )
    blueprint = Blueprint(
        name="python_pytest_unit_test",
        component_type="unit_test",
        required_fields=[],
        quality_requirements=["q"],
        default_invariants=["i"],
    )
    analysis = TargetAnalysis(
        target_path="core/x.py",
        target_import_path="core.x",
        target_kind="class",
        target_name="X",
        public_methods=["run"],
    )

    wo = builder.build(
        request=request,
        blueprint=blueprint,
        analysis=analysis,
        dependency_resolution=ContextDependencyResolution(
            required_read_files=["core/x.py"], helpful_read_files=["core/y.py"]
        ),
    )

    assert wo.payload["target_name"] == "X"
    assert wo.writable_files == ["tests/core/test_x.py"]
    assert any("exactly one file block" in c for c in wo.acceptance_criteria)


def test_builder_edge_cases():
    builder = WorkOrderDraftBuilder()
    blueprint = Blueprint(
        name="python_pytest_unit_test", component_type="unit_test", required_fields=[]
    )
    request = WorkOrderDraftRequest(
        request_id="r",
        blueprint_name="python_pytest_unit_test",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        target_name="X",
        target_kind="class",
        target_import_path="core.x",
        target_path="core/x.py",
        test_path=None,
    )
    analysis = TargetAnalysis(
        target_path="core/x.py",
        target_import_path="core.x",
        target_kind="class",
        target_name="X",
        public_methods=[],
    )

    assert builder._build_goal(
        request=request, blueprint=Blueprint(name="other", component_type="x", required_fields=[])
    ).startswith("Generate artifacts")
    assert (
        builder._infer_responsibility(analysis)
        == "The component exposes a focused public interface."
    )
    assert builder._infer_definition_contract(request, analysis).endswith("stable public API.")
    assert builder._infer_happy_path(request, analysis).startswith("The main behavior")
    assert "deterministically" in builder._infer_error_behavior(request, analysis)

    with pytest.raises(ValueError):
        builder._build_writable_files(request=request, blueprint=blueprint)
    assert (
        builder._build_writable_files(
            request=request,
            blueprint=Blueprint(name="other", component_type="x", required_fields=[]),
        )
        == []
    )

    with pytest.raises(ValueError):
        builder._build_payload(
            request=request,
            blueprint=Blueprint(name="other", component_type="x", required_fields=[]),
            analysis=analysis,
        )
