import importlib


def test_import_work_order_type_module():
    module = importlib.import_module("core.models.work_order_type")
    assert module is not None


def test_work_order_type_exports_expected_symbols():
    module = importlib.import_module("core.models.work_order_type")
    assert hasattr(module, "WorkOrderType")
