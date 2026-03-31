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


def test_build_candidate_paths_and_infer_methods(tmp_path):
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
