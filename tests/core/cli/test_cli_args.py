import importlib


def test_import_cli_args_module():
    module = importlib.import_module("core.cli.cli_args")
    assert module is not None


def test_cli_args_exports_expected_symbols():
    module = importlib.import_module("core.cli.cli_args")
    assert hasattr(module, "CliArgsParser")
