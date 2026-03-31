import importlib


def test_import_atomic_task_loader_module():
    module = importlib.import_module("core.loaders.atomic_task_loader")
    assert module is not None


def test_atomic_task_loader_exports_expected_symbols():
    module = importlib.import_module("core.loaders.atomic_task_loader")
    assert hasattr(module, "AtomicTaskLoader")
