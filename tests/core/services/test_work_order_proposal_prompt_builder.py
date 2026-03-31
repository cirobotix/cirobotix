import importlib


def test_import_work_order_proposal_prompt_builder_module():
    module = importlib.import_module("core.services.work_order_proposal_prompt_builder")
    assert module is not None


def test_work_order_proposal_prompt_builder_exports_expected_symbols():
    module = importlib.import_module("core.services.work_order_proposal_prompt_builder")
    assert hasattr(module, "WorkOrderProposalPromptBuilder")
