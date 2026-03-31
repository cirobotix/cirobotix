import importlib


def test_import_work_order_module():
    module = importlib.import_module("core.models.work_order")
    assert module is not None


def test_work_order_exports_expected_symbols():
    module = importlib.import_module("core.models.work_order")
    assert hasattr(module, "WorkOrder")
