class WorkOrderProposalExecutor:
    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "The 'openai' package is required to run WorkOrderProposalExecutor. "
                "Install project dependencies before executing this step."
            ) from exc
        self.client = OpenAI()

    def generate(self, *, model: str, prompt: str) -> str:
        response = self.client.responses.create(
            model=model,
            input=prompt,
        )

        output_text = getattr(response, "output_text", None)
        if not output_text:
            output_text = str(response)

        return output_text
