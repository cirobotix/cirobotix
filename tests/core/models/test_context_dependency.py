import importlib


def test_import_context_dependency_module():
    module = importlib.import_module("core.models.context_dependency")
    assert module is not None


def test_context_dependency_exports_expected_symbols():
    module = importlib.import_module("core.models.context_dependency")
    assert hasattr(module, "ContextDependency")
    assert hasattr(module, "ContextDependencyResolution")
