import importlib


def test_import_validator_module():
    module = importlib.import_module("core.services.validator")
    assert module is not None


def test_validator_exports_expected_symbols():
    module = importlib.import_module("core.services.validator")
    assert hasattr(module, "Validator")
