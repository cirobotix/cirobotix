import sys
from types import SimpleNamespace

import pytest

from core.services.work_order_proposal_executor import WorkOrderProposalExecutor


class DummyClient:
    @property
    def responses(self):
        return self

    def create(self, *, model, input):  # noqa: A002
        return SimpleNamespace(output_text=f"{model}:{input}")


def test_generate_happy_path_uses_output_text():
    executor = WorkOrderProposalExecutor.__new__(WorkOrderProposalExecutor)
    executor.client = DummyClient()

    result = executor.generate(model="m", prompt="p")

    assert result == "m:p"


def test_generate_falls_back_to_str_response():
    executor = WorkOrderProposalExecutor.__new__(WorkOrderProposalExecutor)

    class FallbackClient(DummyClient):
        def create(self, *, model, input):  # noqa: A002
            return {"result": "ok"}

    executor.client = FallbackClient()

    assert executor.generate(model="m", prompt="p") == "{'result': 'ok'}"


def test_init_handles_openai_present_and_missing(monkeypatch):
    class OpenAIStub:
        pass

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=OpenAIStub))
    executor = WorkOrderProposalExecutor()
    assert isinstance(executor.client, OpenAIStub)

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ModuleNotFoundError("openai")
        return original_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "openai", raising=False)
    monkeypatch.setattr("builtins.__import__", fake_import)
    with pytest.raises(RuntimeError):
        WorkOrderProposalExecutor()
