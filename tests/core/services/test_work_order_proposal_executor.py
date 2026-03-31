from types import SimpleNamespace

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
