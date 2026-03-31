import importlib


def test_import_context_module():
    module = importlib.import_module("core.models.context")
    assert module is not None


def test_context_exports_expected_symbols():
    module = importlib.import_module("core.models.context")
    assert hasattr(module, "ProductionContext")
