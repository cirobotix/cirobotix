from core.models.project_context import ProjectContext
from core.models.target_analysis import TargetAnalysis
from core.services.context_dependency_resolver import ContextDependencyResolver


def test_context_dependency_resolver_happy_and_edge_cases(tmp_path):
    (tmp_path / "core/models").mkdir(parents=True)
    for name in ["context.py", "project_context.py", "work_order.py", "profile.py", "blueprint.py"]:
        (tmp_path / "core/models" / name).write_text("x", encoding="utf-8")

    resolver = ContextDependencyResolver()
    analysis = TargetAnalysis(
        target_path="core/x.py",
        target_import_path="core.x",
        target_kind="class",
        target_name="X",
        direct_project_imports=["core/y.py"],
        referenced_symbols=["context.work_order", "", "unknown.symbol"],
    )
    result = resolver.resolve(project=ProjectContext(root_path=tmp_path), analysis=analysis)

    assert "core/x.py" in result.required_read_files
    assert any(dep.priority == "helpful" for dep in result.dependencies)
    assert resolver._infer_path_from_symbol("", ProjectContext(root_path=tmp_path)) is None
    assert resolver._infer_path_from_symbol("abc.def", ProjectContext(root_path=tmp_path)) is None
