from types import SimpleNamespace

import pytest

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.registry.registry import Registry
from core.services.validator import Validator


def _context(tmp_path, **kwargs):
    work_order = WorkOrder(
        request_id=kwargs.get("request_id", "r"),
        blueprint_name="bp",
        profile_name=kwargs.get("profile_name", "default"),
        order_type=kwargs.get("order_type", WorkOrderType.CREATE),
        goal=kwargs.get("goal", "g"),
        payload=kwargs.get("payload", {"required": "ok"}),
        read_files=kwargs.get("read_files", []),
        writable_files=kwargs.get("writable_files", []),
        invariants=[],
        acceptance_criteria=[],
    )
    return ProductionContext(
        blueprint=Blueprint(name="bp", component_type="x", required_fields=["required"]),
        work_order=work_order,
        profile=ProductionProfile(),
        project=ProjectContext(root_path=tmp_path, protected_files=["protected.py"]),
    )


def test_validator_happy_path(tmp_path):
    registry = Registry()
    registry.register(Blueprint(name="bp", component_type="x", required_fields=["required"]))
    ctx = _context(tmp_path)

    assert Validator(registry).run(ctx) is ctx


def test_validator_error_cases(tmp_path):
    registry = Registry()
    registry.register(Blueprint(name="bp", component_type="x", required_fields=["required"]))

    with pytest.raises(ValueError):
        Validator(registry).run(_context(tmp_path, payload={}))

    with pytest.raises(ValueError):
        Validator(registry).run(_context(tmp_path, request_id=" "))

    with pytest.raises(ValueError):
        Validator(registry).run(_context(tmp_path, profile_name=" "))

    with pytest.raises(ValueError):
        Validator(registry).run(_context(tmp_path, goal=" "))

    with pytest.raises(ValueError):
        Validator(registry).run(_context(tmp_path, read_files=[" "]))

    with pytest.raises(ValueError):
        Validator(registry).run(
            _context(tmp_path, order_type=WorkOrderType.MODIFY, writable_files=[])
        )

    with pytest.raises(ValueError):
        Validator(registry).run(_context(tmp_path, writable_files=["protected.py"]))

    with pytest.raises(ValueError):
        Validator(registry).run(_context(tmp_path, read_files=["missing.py"]))


def test_validator_structure_type_guards(tmp_path):
    registry = Registry()
    registry.register(Blueprint(name="bp", component_type="x", required_fields=[]))
    base_project = ProjectContext(root_path=tmp_path)

    bad_cases = [
        SimpleNamespace(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            goal="g",
            read_files="no-list",
            writable_files=[],
            invariants=[],
            acceptance_criteria=[],
            payload={},
            order_type=WorkOrderType.CREATE,
        ),
        SimpleNamespace(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            goal="g",
            read_files=[],
            writable_files="no-list",
            invariants=[],
            acceptance_criteria=[],
            payload={},
            order_type=WorkOrderType.CREATE,
        ),
        SimpleNamespace(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            goal="g",
            read_files=[],
            writable_files=[],
            invariants="no-list",
            acceptance_criteria=[],
            payload={},
            order_type=WorkOrderType.CREATE,
        ),
        SimpleNamespace(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            goal="g",
            read_files=[],
            writable_files=[],
            invariants=[],
            acceptance_criteria="no-list",
            payload={},
            order_type=WorkOrderType.CREATE,
        ),
        SimpleNamespace(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            goal="g",
            read_files=[],
            writable_files=[],
            invariants=[],
            acceptance_criteria=[],
            payload=[],
            order_type=WorkOrderType.CREATE,
        ),
    ]

    for bad_work_order in bad_cases:
        context = ProductionContext(
            blueprint=Blueprint(name="bp", component_type="x", required_fields=[]),
            work_order=bad_work_order,
            profile=ProductionProfile(),
            project=base_project,
        )
        with pytest.raises(ValueError):
            Validator(registry).run(context)
