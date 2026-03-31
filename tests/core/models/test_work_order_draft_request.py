import importlib


def test_import_work_order_draft_request_module():
    module = importlib.import_module("core.models.work_order_draft_request")
    assert module is not None


def test_work_order_draft_request_exports_expected_symbols():
    module = importlib.import_module("core.models.work_order_draft_request")
    assert hasattr(module, "WorkOrderDraftRequest")
