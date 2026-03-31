from pathlib import Path
from types import SimpleNamespace

from core.models.atomic_task import AtomicTask
from core.models.blueprint import Blueprint
from core.models.context_dependency import ContextDependencyResolution
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.work_order_proposal_service import WorkOrderProposalService


class DummyRegistry:
    def __init__(self, blueprint):
        self.blueprint = blueprint

    def get(self, _name):
        return self.blueprint


def test_init_and_create_registry(monkeypatch):
    import core.services.work_order_proposal_service as mod

    monkeypatch.setattr(
        mod, "WorkOrderProposalExecutor", lambda: SimpleNamespace(generate=lambda **_: "x")
    )
    service = WorkOrderProposalService()
    registry = service.create_registry()
    assert registry is not None


def test_create_ai_proposal_happy_path(tmp_path):
    svc = WorkOrderProposalService.__new__(WorkOrderProposalService)
    blueprint = Blueprint(
        name="python_pytest_unit_test",
        component_type="unit_test",
        required_fields=[],
        default_invariants=["inv"],
    )
    task = AtomicTask(
        task_id="t1",
        blueprint_name="python_pytest_unit_test",
        title="title",
        description="desc",
        inputs={
            "target_path": "core/models/work_order.py",
            "target_import_path": "core.models.work_order",
            "target_kind": "class",
            "target_name": "WorkOrder",
            "test_path": "tests/core/models/test_work_order.py",
        },
        acceptance_criteria=["a1"],
    )

    svc.atomic_task_loader = SimpleNamespace(load=lambda _p: task)
    svc.create_registry = lambda: DummyRegistry(blueprint)
    svc.project_loader = SimpleNamespace(load=lambda _p: ProjectContext(root_path=tmp_path))
    svc.profile_loader = SimpleNamespace(load=lambda _p: ProductionProfile(llm_model="model"))
    svc.target_inspector = SimpleNamespace(
        inspect=lambda **_: SimpleNamespace(
            target_path="x", direct_project_imports=[], referenced_symbols=[]
        )
    )
    svc.dependency_resolver = SimpleNamespace(
        resolve=lambda **_: ContextDependencyResolution(
            required_read_files=["core/models/work_order.py"],
            helpful_read_files=["core/models/context.py"],
        )
    )
    svc.context_assembler = SimpleNamespace(run=lambda ctx: ctx)
    svc.prompt_builder = SimpleNamespace(build=lambda **_: "PROMPT")
    svc.executor = SimpleNamespace(generate=lambda **_: "proposal: yaml")
    svc.writer = SimpleNamespace(write=lambda **_: Path(".codegen/requests/t1/proposal.yaml"))

    result = svc.create_ai_proposal(task_path="x.yaml")

    assert result.endswith("proposal.yaml")


def test_promote_proposal_happy_path(tmp_path):
    svc = WorkOrderProposalService.__new__(WorkOrderProposalService)
    blueprint = Blueprint(
        name="python_pytest_unit_test", component_type="unit_test", required_fields=[]
    )
    work_order = WorkOrder(
        request_id="id1",
        blueprint_name="python_pytest_unit_test",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        goal="g",
        payload={},
    )

    proposal = tmp_path / "proposal.yaml"
    proposal.write_text("x", encoding="utf-8")

    svc.create_registry = lambda: DummyRegistry(blueprint)
    svc.project_loader = SimpleNamespace(load=lambda _p: ProjectContext(root_path=tmp_path))
    svc.work_order_loader = SimpleNamespace(load=lambda _p: work_order)

    promoted = svc.promote_proposal(proposal_path=str(proposal), project_config_path="p")

    assert Path(promoted).exists()
    assert (proposal.parent / "review.md").exists()
