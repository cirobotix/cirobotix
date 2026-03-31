import importlib


def test_import_prompt_module():
    module = importlib.import_module("core.services.prompt")
    assert module is not None


def test_prompt_exports_expected_symbols():
    module = importlib.import_module("core.services.prompt")
    assert hasattr(module, "PromptBuilder")
