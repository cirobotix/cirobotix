from openai import OpenAI


class WorkOrderProposalExecutor:
    def __init__(self) -> None:
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
