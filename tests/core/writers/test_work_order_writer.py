import importlib


def test_import_work_order_writer_module():
    module = importlib.import_module("core.writers.work_order_writer")
    assert module is not None


def test_work_order_writer_exports_expected_symbols():
    module = importlib.import_module("core.writers.work_order_writer")
    assert hasattr(module, "WorkOrderWriter")
