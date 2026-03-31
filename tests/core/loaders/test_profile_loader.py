import importlib


def test_import_profile_loader_module():
    module = importlib.import_module("core.loaders.profile_loader")
    assert module is not None


def test_profile_loader_exports_expected_symbols():
    module = importlib.import_module("core.loaders.profile_loader")
    assert hasattr(module, "ProfileLoader")
