import importlib


def test_import_work_order_draft_builder_module():
    module = importlib.import_module("core.services.work_order_draft_builder")
    assert module is not None


def test_work_order_draft_builder_exports_expected_symbols():
    module = importlib.import_module("core.services.work_order_draft_builder")
    assert hasattr(module, "WorkOrderDraftBuilder")
