import importlib


def test_import_checker_module():
    module = importlib.import_module("core.checkers.checker")
    assert module is not None


def test_checker_exports_expected_symbols():
    module = importlib.import_module("core.checkers.checker")
    assert hasattr(module, "OutputChecker")
