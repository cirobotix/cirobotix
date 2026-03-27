from core.artifact import ArtifactType, ArtifactRequest
from core.registry import Registry
from core.validator import Validator
from core.prompt import PromptBuilder
from core.review import ReviewBuilder
from core.writer import Writer
from core.executor import Executor
from core.checker import OutputChecker


def run() -> None:
    registry = Registry()

    registry.register(
        ArtifactType(
            name="python_registry_class",
            required_fields=[
                "class_name",
                "target_path",
                "test_path",
                "methods",
                "responsibility",
                "definition_contract",
                "get_behavior",
                "list_behavior",
            ],
            description="A bounded Python registry class for a console application.",
        )
    )

    request = ArtifactRequest(
        request_id="test_002",
        artifact_type="python_registry_class",
        payload={
            "class_name": "ArtifactRegistry",
            "target_path": "tool/core/generated_registry.py",
            "test_path": "tests/core/test_generated_registry.py",
            "responsibility": "Register and retrieve artifact definitions for the CLI tool.",
            "methods": [
                "register(definition)",
                "get(name)",
                "list_names()",
            ],
            "definition_contract": "definition must expose a non-empty string attribute 'name'",
            "get_behavior": "raise KeyError if the requested name does not exist",
            "list_behavior": "return all registered names sorted ascending",
        },
    )

    validator = Validator(registry)
    validator.validate(request)

    prompt = PromptBuilder().build(request)
    review = ReviewBuilder().build(request)

    Writer().write(request, prompt, review)

    output_path = Executor().run(request.request_id, model="gpt-4o-mini")
    print(f"LLM output written to: {output_path}")

    OutputChecker().check(request.request_id)


if __name__ == "__main__":
    run()
