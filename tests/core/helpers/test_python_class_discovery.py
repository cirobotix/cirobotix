import importlib


def test_import_python_class_discovery_module():
    module = importlib.import_module("core.helpers.python_class_discovery")
    assert module is not None


def test_python_class_discovery_exports_expected_symbols():
    module = importlib.import_module("core.helpers.python_class_discovery")
    assert hasattr(module, "PythonClassDiscovery")
