
import pytest

from cirobotix.cli import _parse_bool
from cirobotix.scaffolds import ProjectScaffolder


def test_scaffolder_apply_creates_codegen_and_tasks(tmp_path):
    result = ProjectScaffolder().apply(target_dir=tmp_path)

    assert (tmp_path / ".codegen").exists()
    assert (tmp_path / "tasks").exists()
    assert (tmp_path / ".codegen" / "README.md").exists()
    assert (tmp_path / "tasks" / "test_output_checker.yaml").exists()
    assert len(result.created) >= 2


def test_scaffolder_apply_dry_run_does_not_write_files(tmp_path):
    result = ProjectScaffolder().apply(target_dir=tmp_path, dry_run=True)

    assert not (tmp_path / ".codegen").exists()
    assert not (tmp_path / "tasks").exists()
    assert len(result.created) >= 2


def test_scaffolder_respects_force_flag(tmp_path):
    target = tmp_path / "tasks" / "test_output_checker.yaml"
    target.parent.mkdir(parents=True)
    target.write_text("original", encoding="utf-8")

    skipped = ProjectScaffolder().apply(target_dir=tmp_path, force=False)
    assert target in skipped.skipped
    assert target.read_text(encoding="utf-8") == "original"

    overwritten = ProjectScaffolder().apply(target_dir=tmp_path, force=True)
    assert target in overwritten.overwritten
    assert "task_id: test_output_checker" in target.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("1", True),
        ("false", False),
        ("0", False),
    ],
)
def test_parse_bool(value, expected):
    assert _parse_bool({"flag": value}, "flag") is expected


def test_parse_bool_rejects_invalid_value():
    with pytest.raises(ValueError):
        _parse_bool({"flag": "maybe"}, "flag")
