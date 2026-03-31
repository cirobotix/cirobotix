import importlib


def test_import_work_order_loader_module():
    module = importlib.import_module("core.loaders.work_order_loader")
    assert module is not None


def test_work_order_loader_exports_expected_symbols():
    module = importlib.import_module("core.loaders.work_order_loader")
    assert hasattr(module, "WorkOrderLoader")
