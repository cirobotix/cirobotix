import importlib


def test_import_writer_module():
    module = importlib.import_module("core.services.writer")
    assert module is not None


def test_writer_exports_expected_symbols():
    module = importlib.import_module("core.services.writer")
    assert hasattr(module, "Writer")
