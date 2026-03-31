import importlib


def test_import_executor_module():
    module = importlib.import_module("core.services.executor")
    assert module is not None


def test_executor_exports_expected_symbols():
    module = importlib.import_module("core.services.executor")
    assert hasattr(module, "Executor")
