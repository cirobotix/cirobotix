import importlib


def test_import_project_context_module():
    module = importlib.import_module("core.models.project_context")
    assert module is not None


def test_project_context_exports_expected_symbols():
    module = importlib.import_module("core.models.project_context")
    assert hasattr(module, "ProjectContext")
