import importlib


def test_import_target_analysis_module():
    module = importlib.import_module("core.models.target_analysis")
    assert module is not None


def test_target_analysis_exports_expected_symbols():
    module = importlib.import_module("core.models.target_analysis")
    assert hasattr(module, "MethodAnalysis")
    assert hasattr(module, "ImportAnalysis")
    assert hasattr(module, "TargetAnalysis")
