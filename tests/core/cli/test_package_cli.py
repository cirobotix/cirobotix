import importlib


def test_import_package_cli_module():
    module = importlib.import_module("cirobotix.cli")
    assert module is not None


def test_package_cli_exports_main():
    module = importlib.import_module("cirobotix.cli")
    assert hasattr(module, "main")
