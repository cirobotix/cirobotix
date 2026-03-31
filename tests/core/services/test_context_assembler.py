import importlib


def test_import_context_assembler_module():
    module = importlib.import_module("core.services.context_assembler")
    assert module is not None


def test_context_assembler_exports_expected_symbols():
    module = importlib.import_module("core.services.context_assembler")
    assert hasattr(module, "ContextAssembler")
