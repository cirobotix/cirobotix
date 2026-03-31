import importlib


def test_import_request_id_builder_module():
    module = importlib.import_module("core.helpers.request_id_builder")
    assert module is not None


def test_request_id_builder_exports_expected_symbols():
    module = importlib.import_module("core.helpers.request_id_builder")
    assert hasattr(module, "RequestIdBuilder")
