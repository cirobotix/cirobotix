from pathlib import Path

import pytest

from core.checkers.checker import OutputChecker
from core.cli.cli_args import CliArgsParser
from core.formatters.formatter import Formatter
from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType


def _build_context(*, writable_files: list[str], use_formatter: bool = False) -> ProductionContext:
    return ProductionContext(
        blueprint=Blueprint(name="bp", component_type="c", required_fields=[]),
        work_order=WorkOrder(
            request_id="req1",
            blueprint_name="bp",
            profile_name="p",
            order_type=WorkOrderType.CREATE,
            goal="g",
            payload={},
            writable_files=writable_files,
        ),
        profile=ProductionProfile(use_code_formatter=use_formatter),
        project=ProjectContext(root_path=Path(".")),
    )


def test_cli_args_parser_parses_valid_pairs_and_strips_values():
    parsed = CliArgsParser().parse(["key = value", "another=123"])

    assert parsed == {"key": "value", "another": "123"}


def test_cli_args_parser_uses_sys_argv_when_argv_is_none(monkeypatch):
    monkeypatch.setattr("sys.argv", ["prog", "a=1"])

    assert CliArgsParser().parse() == {"a": "1"}


@pytest.mark.parametrize(
    "argv, message",
    [
        (["invalid"], "Argument must be key=value"),
        ([" =v"], "Argument key must not be empty"),
        (["k=   "], "Argument value must not be empty"),
    ],
)
def test_cli_args_parser_raises_for_invalid_inputs(argv, message):
    with pytest.raises(ValueError, match=message):
        CliArgsParser().parse(argv)


def test_output_checker_extract_and_python_checks_cover_edge_cases():
    checker = OutputChecker()

    files = checker._extract_files("### FILE: a.py\n```\nprint('x')\n```")
    assert files == {"a.py": "print('x')"}

    assert checker._check_generic_file("note.txt", "hello") == []
    assert checker._check_python_file("a.py", "```nested```") == [
        "Nested code fence found in file block: a.py"
    ]


def test_output_checker_run_happy_path(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = tmp_path / ".codegen" / "requests" / "req1"
    base.mkdir(parents=True)
    (base / "response.md").write_text(
        "### FILE: src/out.py\n```python\nprint('ok')\n```\n"
        "### FILE: notes.txt\n```\nhello\n```\n",
        encoding="utf-8",
    )
    context = _build_context(writable_files=["src/out.py", "notes.txt"])

    assert OutputChecker().run(context) is context


def test_output_checker_run_raises_when_response_missing(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="response.md not found"):
        OutputChecker().run(_build_context(writable_files=[]))


def test_output_checker_run_reports_missing_unexpected_and_empty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = tmp_path / ".codegen" / "requests" / "req1"
    base.mkdir(parents=True)
    (base / "response.md").write_text(
        "### FILE: expected.py\n```python\n   \n```\n"
        "### FILE: extra.py\n```python\nprint('x')\n```\n",
        encoding="utf-8",
    )
    context = _build_context(writable_files=["expected.py", "missing.py"])

    with pytest.raises(ValueError, match="Output validation failed"):
        OutputChecker().run(context)


def test_formatter_skips_when_disabled():
    context = _build_context(writable_files=[])

    assert Formatter().run(context) is context


def test_formatter_requires_command_when_enabled():
    context = _build_context(writable_files=["a.py"], use_formatter=True)

    with pytest.raises(ValueError, match="no formatter_command"):
        Formatter().run(context)


def test_formatter_requires_written_files_when_enabled_with_command():
    context = _build_context(writable_files=[], use_formatter=True)
    context.profile = ProductionProfile(use_code_formatter=True, formatter_command=["black"])

    with pytest.raises(ValueError, match="No written files available"):
        Formatter().run(context)


def test_formatter_raises_on_non_zero_return_code(monkeypatch):
    context = _build_context(writable_files=[], use_formatter=True)
    context.profile = ProductionProfile(use_code_formatter=True, formatter_command=["black"])
    context.written_files = [Path("a.py")]

    class Result:
        returncode = 2

    def fake_run(command, check):
        assert command == ["black", "a.py"]
        assert check is False
        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)

    with pytest.raises(RuntimeError, match="Formatter failed with exit code 2"):
        Formatter().run(context)


def test_formatter_runs_successfully(monkeypatch):
    context = _build_context(writable_files=[], use_formatter=True)
    context.profile = ProductionProfile(use_code_formatter=True, formatter_command=["ruff", "format"])
    context.written_files = [Path("a.py"), Path("b.py")]

    class Result:
        returncode = 0

    monkeypatch.setattr("subprocess.run", lambda command, check: Result())

    assert Formatter().run(context) is context
