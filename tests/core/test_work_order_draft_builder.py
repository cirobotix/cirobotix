from pathlib import Path

from core.blueprints.python_pytest_unit_test import build_python_pytest_unit_test_blueprint
from core.context_dependency_resolver import ContextDependencyResolver
from core.project_context import ProjectContext
from core.target_inspector import TargetInspector
from core.work_order_draft_builder import WorkOrderDraftBuilder
from core.work_order_draft_request import WorkOrderDraftRequest
from core.work_order_type import WorkOrderType


def test_build_pytest_unit_test_work_order_from_analysis_and_dependencies():
    project = ProjectContext(root_path=Path(".").resolve())
    inspector = TargetInspector()
    resolver = ContextDependencyResolver()
    builder = WorkOrderDraftBuilder()
    blueprint = build_python_pytest_unit_test_blueprint()

    analysis = inspector.inspect(
        project=project,
        target_path="core/applier.py",
        target_import_path="core.applier",
        target_kind="class",
        target_name="OutputApplier",
    )

    resolution = resolver.resolve(
        project=project,
        analysis=analysis,
    )

    request = WorkOrderDraftRequest(
        request_id="applier_unit_test_draft",
        blueprint_name="python_pytest_unit_test",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        target_name="OutputApplier",
        target_kind="class",
        target_import_path="core.applier",
        target_path="core/applier.py",
        test_path="tests/core/test_applier.py",
    )

    work_order = builder.build(
        request=request,
        blueprint=blueprint,
        analysis=analysis,
        dependency_resolution=resolution,
    )

    assert work_order.request_id == "applier_unit_test_draft"
    assert work_order.blueprint_name == "python_pytest_unit_test"
    assert work_order.writable_files == ["tests/core/test_applier.py"]

    assert "core/applier.py" in work_order.read_files
    assert "core/context.py" in work_order.read_files

    assert work_order.payload["target_name"] == "OutputApplier"
    assert work_order.payload["target_import_path"] == "core.applier"
    assert work_order.payload["target_path"] == "core/applier.py"
    assert work_order.payload["test_path"] == "tests/core/test_applier.py"


def test_build_pytest_unit_test_work_order_requires_test_path():
    project = ProjectContext(root_path=Path(".").resolve())
    inspector = TargetInspector()
    resolver = ContextDependencyResolver()
    builder = WorkOrderDraftBuilder()
    blueprint = build_python_pytest_unit_test_blueprint()

    analysis = inspector.inspect(
        project=project,
        target_path="core/applier.py",
        target_import_path="core.applier",
        target_kind="class",
        target_name="OutputApplier",
    )

    resolution = resolver.resolve(
        project=project,
        analysis=analysis,
    )

    request = WorkOrderDraftRequest(
        request_id="applier_unit_test_draft",
        blueprint_name="python_pytest_unit_test",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        target_name="OutputApplier",
        target_kind="class",
        target_import_path="core.applier",
        target_path="core/applier.py",
        test_path=None,
    )

    try:
        builder.build(
            request=request,
            blueprint=blueprint,
            analysis=analysis,
            dependency_resolution=resolution,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "test_path is required" in str(exc)
