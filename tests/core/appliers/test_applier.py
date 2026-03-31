import importlib


def test_import_applier_module():
    module = importlib.import_module("core.appliers.applier")
    assert module is not None


def test_applier_exports_expected_symbols():
    module = importlib.import_module("core.appliers.applier")
    assert hasattr(module, "OutputApplier")
