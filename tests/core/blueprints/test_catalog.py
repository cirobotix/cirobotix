import importlib


def test_import_catalog_module():
    module = importlib.import_module("core.blueprints.catalog")
    assert module is not None


def test_catalog_exports_expected_symbols():
    module = importlib.import_module("core.blueprints.catalog")
    assert hasattr(module, "register_blueprints")
