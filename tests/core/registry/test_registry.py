import importlib


def test_import_registry_module():
    module = importlib.import_module("core.registry.registry")
    assert module is not None


def test_registry_exports_expected_symbols():
    module = importlib.import_module("core.registry.registry")
    assert hasattr(module, "Registry")
