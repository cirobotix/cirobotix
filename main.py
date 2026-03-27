from core.blueprint import Blueprint
from core.artifact import ArtifactRequest
from core.registry import Registry
from core.validator import Validator
from core.prompt import PromptBuilder
from core.review import ReviewBuilder
from core.writer import Writer
from core.executor import Executor
from core.checker import OutputChecker
from core.applier import OutputApplier
from core.test_runner import TestRunner


def run() -> None:
    registry = Registry()

    registry.register(
        Blueprint(
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
            output_files=[
                "core/generated_registry.py",
                "tests/core/test_generated_registry.py",
            ],
            constraints=[
                "Generate exactly one Python class in the source file",
                "Do not create unrelated helper classes",
                "Use type hints",
                "Include a class docstring",
                "Do not add external dependencies",
            ],
            quality_requirements=[
                "The test file must import pytest",
                "The test file must import ArtifactRegistry from core.generated_registry",
                "At least 3 pytest test functions must be generated",
            ],
        )
    )

    request = ArtifactRequest(
        request_id="test_002",
        blueprint_name="python_registry_class",
        payload={
            "class_name": "ArtifactRegistry",
            "target_path": "core/generated_registry.py",
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

    written_files = OutputApplier().apply(request.request_id)
    print("\n✅ APPLIED FILES:")
    for file_path in written_files:
        print(f"- {file_path}")

    print("\n🧪 RUNNING TESTS...")
    TestRunner().run()
    print("✅ TESTS PASSED")


if __name__ == "__main__":
    run()
