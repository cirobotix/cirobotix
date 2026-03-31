import importlib


def test_import_result_module():
    module = importlib.import_module("core.models.result")
    assert module is not None


def test_result_exports_expected_symbols():
    module = importlib.import_module("core.models.result")
    assert hasattr(module, "StepResult")
