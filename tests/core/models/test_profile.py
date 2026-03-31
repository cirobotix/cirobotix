import importlib


def test_import_profile_module():
    module = importlib.import_module("core.models.profile")
    assert module is not None


def test_profile_exports_expected_symbols():
    module = importlib.import_module("core.models.profile")
    assert hasattr(module, "ProductionProfile")
