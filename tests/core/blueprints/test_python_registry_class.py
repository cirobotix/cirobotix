import importlib


def test_import_python_registry_class_module():
    module = importlib.import_module("core.blueprints.python_registry_class")
    assert module is not None


def test_python_registry_class_exports_expected_symbols():
    module = importlib.import_module("core.blueprints.python_registry_class")
    assert hasattr(module, "build_python_registry_class_blueprint")
