from pathlib import Path

from core.models.project_context import ProjectContext
from core.services.target_inspector import TargetInspector


def test_inspect_output_applier_class_extracts_public_methods_and_project_imports():
    project = ProjectContext(root_path=Path(".").resolve())
    inspector = TargetInspector()

    analysis = inspector.inspect(
        project=project,
        target_path="core/applier.py",
        target_import_path="core.applier",
        target_kind="class",
        target_name="OutputApplier",
    )

    assert analysis.class_name == "OutputApplier"
    assert "run" in analysis.public_methods
    assert "core/context.py" in analysis.direct_project_imports


def test_inspect_output_applier_collects_context_related_symbols():
    project = ProjectContext(root_path=Path(".").resolve())
    inspector = TargetInspector()

    analysis = inspector.inspect(
        project=project,
        target_path="core/applier.py",
        target_import_path="core.applier",
        target_kind="class",
        target_name="OutputApplier",
    )

    assert "ProductionContext" in analysis.referenced_symbols
    assert "context.work_order" in analysis.referenced_symbols
    assert "context.written_files" in analysis.referenced_symbols
