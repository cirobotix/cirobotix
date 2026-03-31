import importlib


def test_import_python_pytest_unit_test_module():
    module = importlib.import_module("core.blueprints.python_pytest_unit_test")
    assert module is not None


def test_python_pytest_unit_test_exports_expected_symbols():
    module = importlib.import_module("core.blueprints.python_pytest_unit_test")
    assert hasattr(module, "build_python_pytest_unit_test_blueprint")
