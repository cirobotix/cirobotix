from types import SimpleNamespace

import pytest

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.work_order_cli_service import WorkOrderCliService


class DummyRegistry:
    def __init__(self, blueprint):
        self.blueprint = blueprint

    def get(self, _name):
        return self.blueprint


def test_create_draft_happy_path(tmp_path):
    target_file = tmp_path / "core" / "sample.py"
    target_file.parent.mkdir(parents=True)
    target_file.write_text("class Sample:\n    pass\n", encoding="utf-8")

    svc = WorkOrderCliService.__new__(WorkOrderCliService)
    blueprint = Blueprint(
        name="python_pytest_unit_test", component_type="unit_test", required_fields=[]
    )
    svc.create_registry = lambda: DummyRegistry(blueprint)
    svc.project_loader = SimpleNamespace(load=lambda _p: ProjectContext(root_path=tmp_path))
    svc.target_helper = SimpleNamespace(
        to_import_path=lambda _p: "core.sample", to_test_path=lambda _p: "tests/core/test_sample.py"
    )
    svc.class_discovery = SimpleNamespace(find_primary_class_name=lambda _p: "Sample")
    analysis = SimpleNamespace(
        target_path="core/sample.py", direct_project_imports=[], referenced_symbols=[]
    )
    svc.target_inspector = SimpleNamespace(inspect=lambda **_: analysis)
    svc.dependency_resolver = SimpleNamespace(
        resolve=lambda **_: SimpleNamespace(required_read_files=[], helpful_read_files=[])
    )
    work_order = WorkOrder(
        request_id="rid",
        blueprint_name="python_pytest_unit_test",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        goal="g",
        payload={},
    )
    svc.request_id_builder = SimpleNamespace(build=lambda *_: "rid")
    svc.draft_builder = SimpleNamespace(build=lambda **_: work_order)
    svc.work_order_writer = SimpleNamespace(write=lambda *_: None)
    svc.review_writer = SimpleNamespace(write=lambda *_: None)

    path = svc.create_draft(blueprint_name="python_pytest_unit_test", target_path="core/sample.py")

    assert str(path).endswith(".codegen/requests/rid/task.yaml")


def test_init_create_registry_and_missing_target(monkeypatch, tmp_path):
    import core.services.work_order_cli_service as mod

    class DummyExecutor:
        def __init__(self):
            self.called = True

    monkeypatch.setattr(mod, "Executor", DummyExecutor)
    service = WorkOrderCliService()
    registry = service.create_registry()
    assert registry is not None

    service.project_loader = SimpleNamespace(load=lambda _p: ProjectContext(root_path=tmp_path))
    service.create_registry = lambda: DummyRegistry(
        Blueprint(name="python_pytest_unit_test", component_type="unit_test", required_fields=[])
    )
    with pytest.raises(FileNotFoundError):
        service.create_draft(blueprint_name="python_pytest_unit_test", target_path="missing.py")


def test_generate_runs_pipeline(tmp_path):
    svc = WorkOrderCliService.__new__(WorkOrderCliService)
    work_order = WorkOrder(
        request_id="rid",
        blueprint_name="python_pytest_unit_test",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        goal="g",
        payload={},
    )
    blueprint = Blueprint(
        name="python_pytest_unit_test", component_type="unit_test", required_fields=[]
    )
    project = ProjectContext(root_path=tmp_path)
    profile = ProductionProfile()

    svc.work_order_loader = SimpleNamespace(load=lambda _p: work_order)
    svc.project_loader = SimpleNamespace(load=lambda _p: project)
    svc.profile_loader = SimpleNamespace(load=lambda _p: profile)
    svc.create_registry = lambda: DummyRegistry(blueprint)

    import core.services.work_order_cli_service as mod

    original_line = mod.ProductionLine
    original_executor = mod.Executor

    class DummyLine:
        def __init__(self, machines):
            self.machines = machines

        def run(self, context):
            context.add_error("x")
            return context

    mod.ProductionLine = DummyLine
    mod.Executor = lambda: object()
    try:
        result = svc.generate(work_order_path="task.yaml")
    finally:
        mod.ProductionLine = original_line
        mod.Executor = original_executor

    assert isinstance(result, ProductionContext)
    assert result.errors == ["x"]
