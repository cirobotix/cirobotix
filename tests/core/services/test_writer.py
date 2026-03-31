from pathlib import Path

import pytest

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.writer import Writer


def _context(tmp_path):
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
        profile=ProductionProfile(),
        project=ProjectContext(root_path=tmp_path),
    )


def test_writer_happy_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ctx = _context(tmp_path)
    ctx.prompt_text = "prompt"
    ctx.review_text = "review"

    updated = Writer().run(ctx)

    assert updated.base_dir == Path(".codegen") / "requests" / "r"
    assert (updated.base_dir / "task.json").exists()


def test_writer_missing_fields_raise(tmp_path):
    ctx = _context(tmp_path)
    with pytest.raises(ValueError):
        Writer().run(ctx)

    ctx.prompt_text = "prompt"
    with pytest.raises(ValueError):
        Writer().run(ctx)
