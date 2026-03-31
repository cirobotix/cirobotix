import importlib


def test_import_init_module():
    module = importlib.import_module("core.appliers.__init__")
    assert module is not None
