import importlib


def test_import_test_runner_module():
    module = importlib.import_module("core.runners.test_runner")
    assert module is not None


def test_test_runner_exports_expected_symbols():
    module = importlib.import_module("core.runners.test_runner")
    assert hasattr(module, "TestRunner")
