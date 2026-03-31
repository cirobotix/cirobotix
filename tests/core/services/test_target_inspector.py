import importlib


def test_import_target_inspector_module():
    module = importlib.import_module("core.services.target_inspector")
    assert module is not None


def test_target_inspector_exports_expected_symbols():
    module = importlib.import_module("core.services.target_inspector")
    assert hasattr(module, "TargetInspector")
