import pytest

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.context_assembler import ContextAssembler


def _context(tmp_path, read_files):
    return ProductionContext(
        blueprint=Blueprint(name="bp", component_type="x", required_fields=[]),
        work_order=WorkOrder(
            request_id="r",
            blueprint_name="bp",
            profile_name="default",
            order_type=WorkOrderType.CREATE,
            goal="g",
            payload={},
            read_files=read_files,
        ),
        profile=ProductionProfile(),
        project=ProjectContext(root_path=tmp_path),
    )


def test_context_assembler_happy_path(tmp_path):
    file_path = tmp_path / "a.py"
    file_path.write_text("print('x')", encoding="utf-8")
    ctx = _context(tmp_path, ["a.py"])

    updated = ContextAssembler(max_chars_per_file=100).run(ctx)

    assert "## FILE: a.py" in (updated.assembled_context or "")


def test_context_assembler_missing_file_and_truncate(tmp_path):
    ctx = _context(tmp_path, ["missing.py"])
    with pytest.raises(FileNotFoundError):
        ContextAssembler().run(ctx)

    assembler = ContextAssembler(max_chars_per_file=3)
    assert assembler._truncate("abcdef").endswith("# ... truncated ...")
