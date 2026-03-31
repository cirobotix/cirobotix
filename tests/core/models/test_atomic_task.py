import importlib


def test_import_atomic_task_module():
    module = importlib.import_module("core.models.atomic_task")
    assert module is not None


def test_atomic_task_exports_expected_symbols():
    module = importlib.import_module("core.models.atomic_task")
    assert hasattr(module, "AtomicTask")
