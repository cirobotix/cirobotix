from pathlib import Path

from core.context_dependency_resolver import ContextDependencyResolver
from core.project_context import ProjectContext
from core.target_inspector import TargetInspector


def test_resolver_includes_target_and_direct_project_imports():
    project = ProjectContext(root_path=Path(".").resolve())
    inspector = TargetInspector()
    resolver = ContextDependencyResolver()

    analysis = inspector.inspect(
        project=project,
        target_path="core/applier.py",
        target_import_path="core.applier",
        target_kind="class",
        target_name="OutputApplier",
    )

    resolution = resolver.resolve(project=project, analysis=analysis)

    assert "core/applier.py" in resolution.required_read_files
    assert "core/context.py" in resolution.required_read_files


def test_resolver_infers_helpful_context_files_from_symbols():
    project = ProjectContext(root_path=Path(".").resolve())
    inspector = TargetInspector()
    resolver = ContextDependencyResolver()

    analysis = inspector.inspect(
        project=project,
        target_path="core/applier.py",
        target_import_path="core.applier",
        target_kind="class",
        target_name="OutputApplier",
    )

    resolution = resolver.resolve(project=project, analysis=analysis)

    assert "core/work_order.py" in resolution.helpful_read_files
