import importlib


def test_import_project_loader_module():
    module = importlib.import_module("core.loaders.project_loader")
    assert module is not None


def test_project_loader_exports_expected_symbols():
    module = importlib.import_module("core.loaders.project_loader")
    assert hasattr(module, "ProjectLoader")
