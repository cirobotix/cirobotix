import importlib


def test_import_review_module():
    module = importlib.import_module("core.services.review")
    assert module is not None


def test_review_exports_expected_symbols():
    module = importlib.import_module("core.services.review")
    assert hasattr(module, "ReviewBuilder")
