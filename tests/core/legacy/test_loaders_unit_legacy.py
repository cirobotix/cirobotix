from pathlib import Path

import pytest

from core.loaders.atomic_task_loader import AtomicTaskLoader
from core.loaders.profile_loader import ProfileLoader
from core.loaders.project_loader import ProjectLoader
from core.loaders.work_order_loader import WorkOrderLoader
from core.models.work_order_type import WorkOrderType


def test_atomic_task_loader_happy_path_and_defaults(tmp_path: Path):
    file_path = tmp_path / "task.yaml"
    file_path.write_text(
        """
task_id: t1
blueprint_name: bp
title: Do it
description: Desc
""".strip(),
        encoding="utf-8",
    )

    task = AtomicTaskLoader().load(str(file_path))

    assert task.task_id == "t1"
    assert task.inputs == {}
    assert task.acceptance_criteria == []


def test_atomic_task_loader_missing_file_raises():
    with pytest.raises(FileNotFoundError, match="Atomic task file not found"):
        AtomicTaskLoader().load("missing.yaml")


def test_atomic_task_loader_non_mapping_raises(tmp_path: Path):
    file_path = tmp_path / "task.yaml"
    file_path.write_text("- not\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        AtomicTaskLoader().load(str(file_path))


def test_profile_loader_happy_path_and_defaults(tmp_path: Path):
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "dev.yaml").write_text("{}\n", encoding="utf-8")

    profile = ProfileLoader(str(profiles_dir)).load("dev")

    assert profile.llm_model == "gpt-4o-mini"
    assert profile.test_command == ["pytest"]
    assert profile.fail_on_quality_error is True


def test_profile_loader_explicit_values(tmp_path: Path):
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "ci.yaml").write_text(
        """
llm_model: x
run_local_tests: false
test_command: ["pytest", "-q"]
pythonpath_root: src
use_code_formatter: true
formatter_command: ["ruff", "format"]
fail_on_quality_error: false
""".strip(),
        encoding="utf-8",
    )

    profile = ProfileLoader(str(profiles_dir)).load("ci")

    assert profile.llm_model == "x"
    assert profile.run_local_tests is False
    assert profile.test_command == ["pytest", "-q"]
    assert profile.pythonpath_root == "src"
    assert profile.use_code_formatter is True
    assert profile.formatter_command == ["ruff", "format"]
    assert profile.fail_on_quality_error is False


@pytest.mark.parametrize(
    "name, content, error",
    [
        ("", None, "profile_name must be a non-empty string"),
        ("missing", None, "Profile file not found"),
        ("bad", "[]\n", "must contain a YAML mapping"),
    ],
)
def test_profile_loader_validation(tmp_path: Path, name, content, error):
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    if content is not None:
        (profiles_dir / f"{name}.yaml").write_text(content, encoding="utf-8")

    with pytest.raises((ValueError, FileNotFoundError), match=error):
        ProfileLoader(str(profiles_dir)).load(name)


def test_project_loader_happy_path_and_defaults(tmp_path: Path):
    file_path = tmp_path / "project.yaml"
    file_path.write_text("{}\n", encoding="utf-8")

    project = ProjectLoader().load(str(file_path))

    assert isinstance(project.root_path, Path)
    assert project.pythonpath_root == "."
    assert project.source_roots == []


def test_project_loader_with_explicit_values(tmp_path: Path):
    file_path = tmp_path / "project.yaml"
    file_path.write_text(
        """
root_path: .
pythonpath_root: src
source_roots: ["core"]
test_roots: ["tests"]
protected_files: ["README.md"]
""".strip(),
        encoding="utf-8",
    )

    project = ProjectLoader().load(str(file_path))

    assert project.pythonpath_root == "src"
    assert project.source_roots == ["core"]
    assert project.test_roots == ["tests"]
    assert project.protected_files == ["README.md"]


def test_project_loader_validation(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Project config not found"):
        ProjectLoader().load(str(tmp_path / "missing.yaml"))

    bad_path = tmp_path / "project.yaml"
    bad_path.write_text("[]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        ProjectLoader().load(str(bad_path))


def test_work_order_loader_happy_path_and_defaults(tmp_path: Path):
    file_path = tmp_path / "wo.yaml"
    file_path.write_text(
        """
request_id: r1
blueprint_name: bp
profile_name: p
order_type: create
payload: {}
""".strip(),
        encoding="utf-8",
    )

    work_order = WorkOrderLoader().load(str(file_path))

    assert work_order.order_type == WorkOrderType.CREATE
    assert work_order.goal == ""
    assert work_order.read_files == []


def test_work_order_loader_with_explicit_values(tmp_path: Path):
    file_path = tmp_path / "wo.yaml"
    file_path.write_text(
        """
request_id: r1
blueprint_name: bp
profile_name: p
order_type: modify
goal: g
payload: {x: 1}
read_files: ["a"]
writable_files: ["b"]
invariants: ["i"]
acceptance_criteria: ["ac"]
""".strip(),
        encoding="utf-8",
    )

    work_order = WorkOrderLoader().load(str(file_path))

    assert work_order.order_type == WorkOrderType.MODIFY
    assert work_order.goal == "g"
    assert work_order.payload == {"x": 1}
    assert work_order.writable_files == ["b"]
    assert work_order.acceptance_criteria == ["ac"]


def test_work_order_loader_validation_and_invalid_enum(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Work order file not found"):
        WorkOrderLoader().load(str(tmp_path / "missing.yaml"))

    bad_type = tmp_path / "bad.yaml"
    bad_type.write_text("[]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        WorkOrderLoader().load(str(bad_type))

    invalid_enum = tmp_path / "invalid_enum.yaml"
    invalid_enum.write_text(
        """
request_id: r1
blueprint_name: bp
profile_name: p
order_type: invalid
payload: {}
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        WorkOrderLoader().load(str(invalid_enum))
