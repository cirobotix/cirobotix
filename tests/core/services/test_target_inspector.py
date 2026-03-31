import ast

import pytest

from core.models.project_context import ProjectContext
from core.models.target_analysis import ImportAnalysis
from core.services.target_inspector import TargetInspector


def test_annotation_and_find_class_edges(tmp_path):
    inspector = TargetInspector()

    tree = ast.parse("class A:\n    pass\n")
    assert inspector._find_class(tree, "A").name == "A"
    with pytest.raises(ValueError):
        inspector._find_class(tree, "B")

    assert (
        inspector._annotation_to_name(ast.parse("x: list[int]", mode="single").body[0].annotation)
        == "list"
    )
    assert (
        inspector._annotation_to_name(ast.parse('x: "MyType"', mode="single").body[0].annotation)
        == "MyType"
    )
    assert (
        inspector._annotation_to_name(ast.parse("x: pkg.Type", mode="single").body[0].annotation)
        == "pkg.Type"
    )
    assert inspector._annotation_to_name(ast.Constant(value=1)) is None


def test_build_candidate_paths_and_relative_variants(tmp_path):
    inspector = TargetInspector()
    project = ProjectContext(root_path=tmp_path)
    abs_import = inspector._build_candidate_paths(
        project=project,
        item=ImportAnalysis(
            module="a.b", imported_names=["c"], is_relative=False, relative_level=0
        ),
        current_file_path="x.py",
    )
    assert "a/b.py" in abs_import
    assert "a/b/c.py" in abs_import

    rel_import = inspector._build_candidate_paths(
        project=project,
        item=ImportAnalysis(module="", imported_names=[], is_relative=True, relative_level=1),
        current_file_path="core/services/x.py",
    )
    assert rel_import == []

    rel_with_module = inspector._build_relative_candidate_paths(
        item=ImportAnalysis(module="a.b", imported_names=["C"], is_relative=True, relative_level=2),
        current_file_path="core/services/x.py",
    )
    assert "core/a/b.py" in rel_with_module

    rel_without_module = inspector._build_relative_candidate_paths(
        item=ImportAnalysis(module="", imported_names=["util"], is_relative=True, relative_level=1),
        current_file_path="core/services/x.py",
    )
    assert "core/services/util.py" in rel_without_module


def test_inspect_missing_file_and_unsupported_kind(tmp_path):
    inspector = TargetInspector()
    project = ProjectContext(root_path=tmp_path)

    with pytest.raises(FileNotFoundError):
        inspector.inspect(
            project=project,
            target_path="missing.py",
            target_import_path="missing",
            target_kind="class",
            target_name="X",
        )

    file_path = tmp_path / "x.py"
    file_path.write_text("class X:\n    y = 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        inspector.inspect(
            project=project,
            target_path="x.py",
            target_import_path="x",
            target_kind="function",
            target_name="X",
        )
