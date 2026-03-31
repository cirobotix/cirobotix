import importlib


def test_import_machine_module():
    module = importlib.import_module("core.protocols.machine")
    assert module is not None


def test_machine_exports_expected_symbols():
    module = importlib.import_module("core.protocols.machine")
    assert hasattr(module, "Machine")
