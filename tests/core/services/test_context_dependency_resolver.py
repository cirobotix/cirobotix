import importlib


def test_import_context_dependency_resolver_module():
    module = importlib.import_module("core.services.context_dependency_resolver")
    assert module is not None


def test_context_dependency_resolver_exports_expected_symbols():
    module = importlib.import_module("core.services.context_dependency_resolver")
    assert hasattr(module, "ContextDependencyResolver")
