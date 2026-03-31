import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.models.blueprint import Blueprint
from core.models.context import ProductionContext
from core.models.profile import ProductionProfile
from core.models.project_context import ProjectContext
from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.services.executor import Executor


class DummyClient:
    def __init__(self, output_text="RESULT"):
        self.output_text = output_text
        self.last_model = None
        self.last_input = None

    @property
    def responses(self):
        return self

    def create(self, *, model, input):  # noqa: A002
        self.last_model = model
        self.last_input = input
        return SimpleNamespace(output_text=self.output_text)


@pytest.fixture
def context(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    work_order = WorkOrder(
        request_id="req-1",
        blueprint_name="bp",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        goal="g",
        payload={},
    )
    ctx = ProductionContext(
        blueprint=Blueprint(name="bp", component_type="x", required_fields=[]),
        work_order=work_order,
        profile=ProductionProfile(llm_model="gpt-test"),
        project=ProjectContext(root_path=tmp_path),
    )
    base = Path(".codegen/requests/req-1")
    base.mkdir(parents=True)
    (base / "prompt.md").write_text("PROMPT", encoding="utf-8")
    return ctx


def test_run_happy_path_writes_response(context):
    executor = Executor.__new__(Executor)
    executor.client = DummyClient(output_text="AI OUTPUT")

    updated = executor.run(context)

    assert updated.response_path is not None
    assert updated.response_path.read_text(encoding="utf-8") == "AI OUTPUT"


def test_run_without_prompt_file_raises(context):
    prompt_file = Path(".codegen/requests/req-1/prompt.md")
    prompt_file.unlink()
    executor = Executor.__new__(Executor)
    executor.client = DummyClient()

    with pytest.raises(FileNotFoundError):
        executor.run(context)


def test_run_uses_stringified_response_if_output_text_missing(context):
    executor = Executor.__new__(Executor)

    class StringResponseClient(DummyClient):
        def create(self, *, model, input):  # noqa: A002
            self.last_model = model
            self.last_input = input
            return {"data": "fallback"}

    executor.client = StringResponseClient()
    updated = executor.run(context)

    assert updated.response_path.read_text(encoding="utf-8") == "{'data': 'fallback'}"


def test_executor_init_handles_openai_present_and_missing(monkeypatch):
    class OpenAIStub:
        pass

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=OpenAIStub))
    executor = Executor()
    assert isinstance(executor.client, OpenAIStub)

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ModuleNotFoundError("openai")
        return original_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "openai", raising=False)
    monkeypatch.setattr("builtins.__import__", fake_import)
    with pytest.raises(RuntimeError):
        Executor()
