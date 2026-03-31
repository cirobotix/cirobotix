import pytest

from core.checkers.checker import OutputChecker
from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType


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
            writable_files=["out.py"],
        ),
        profile=ProductionProfile(),
        project=ProjectContext(root_path=tmp_path),
    )


def test_output_checker_happy_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = tmp_path / ".codegen" / "requests" / "r"
    base.mkdir(parents=True)
    (base / "response.md").write_text(
        "### FILE: out.py\n```python\nprint('x')\n```", encoding="utf-8"
    )

    assert OutputChecker().run(_context(tmp_path))


def test_output_checker_edge_cases(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ctx = _context(tmp_path)
    checker = OutputChecker()

    with pytest.raises(FileNotFoundError):
        checker.run(ctx)

    base = tmp_path / ".codegen" / "requests" / "r"
    base.mkdir(parents=True)
    (base / "response.md").write_text("### FILE: out.py\n```python\n\n```", encoding="utf-8")
    with pytest.raises(ValueError):
        checker.run(ctx)

    assert "Python file block is empty: out.py" in checker._check_python_file("out.py", "")
