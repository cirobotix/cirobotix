import os
from types import SimpleNamespace

import pytest

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.runners.test_runner import TestRunner


def build_context(run_local_tests=True):
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
        profile=ProductionProfile(
            run_local_tests=run_local_tests,
            pythonpath_root=".",
            test_command=["pytest"],
        ),
        project=ProjectContext(root_path=os.getcwd()),
    )


def test_test_runner_skips_when_disabled():
    ctx = build_context(run_local_tests=False)

    assert TestRunner().run(ctx) is ctx


def test_test_runner_runs_and_handles_failures(monkeypatch):
    ctx = build_context(run_local_tests=True)

    def fake_run(_cmd, env, check):
        assert env["PYTHONPATH"].startswith(".")
        assert check is False
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("subprocess.run", fake_run)

    assert TestRunner().run(ctx) is ctx

    monkeypatch.setattr("subprocess.run", lambda *_args, **_kwargs: SimpleNamespace(returncode=1))
    with pytest.raises(RuntimeError):
        TestRunner().run(ctx)
