import importlib


def test_import_work_order_proposal_executor_module():
    module = importlib.import_module("core.services.work_order_proposal_executor")
    assert module is not None


def test_work_order_proposal_executor_exports_expected_symbols():
    module = importlib.import_module("core.services.work_order_proposal_executor")
    assert hasattr(module, "WorkOrderProposalExecutor")
