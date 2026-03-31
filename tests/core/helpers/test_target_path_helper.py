import importlib


def test_import_target_path_helper_module():
    module = importlib.import_module("core.helpers.target_path_helper")
    assert module is not None


def test_target_path_helper_exports_expected_symbols():
    module = importlib.import_module("core.helpers.target_path_helper")
    assert hasattr(module, "TargetPathHelper")
