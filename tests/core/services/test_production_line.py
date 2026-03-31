import importlib


def test_import_production_line_module():
    module = importlib.import_module("core.services.production_line")
    assert module is not None


def test_production_line_exports_expected_symbols():
    module = importlib.import_module("core.services.production_line")
    assert hasattr(module, "ProductionLine")
