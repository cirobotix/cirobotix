import importlib


def test_import_formatter_module():
    module = importlib.import_module("core.formatters.formatter")
    assert module is not None


def test_formatter_exports_expected_symbols():
    module = importlib.import_module("core.formatters.formatter")
    assert hasattr(module, "Formatter")
