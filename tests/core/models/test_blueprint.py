import importlib


def test_import_blueprint_module():
    module = importlib.import_module("core.models.blueprint")
    assert module is not None


def test_blueprint_exports_expected_symbols():
    module = importlib.import_module("core.models.blueprint")
    assert hasattr(module, "Blueprint")
