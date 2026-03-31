import importlib


def test_import_work_order_cli_service_module():
    module = importlib.import_module("core.services.work_order_cli_service")
    assert module is not None


def test_work_order_cli_service_exports_expected_symbols():
    module = importlib.import_module("core.services.work_order_cli_service")
    assert hasattr(module, "WorkOrderCliService")
