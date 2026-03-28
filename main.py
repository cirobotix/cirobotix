from pathlib import Path

from core.blueprint import Blueprint
from core.context_assembler import ContextAssembler
from core.project_context import ProjectContext
from core.work_order import WorkOrder
from core.profile import ProductionProfile
from core.context import ProductionContext
from core.registry import Registry
from core.validator import Validator
from core.prompt import PromptBuilder
from core.review import ReviewBuilder
from core.work_order_type import WorkOrderType
from core.writer import Writer
from core.executor import Executor
from core.checker import OutputChecker
from core.applier import OutputApplier
from core.test_runner import TestRunner
from core.production_line import ProductionLine
from core.formatter import Formatter


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

    profile = ProductionProfile(
        llm_model="gpt-4o-mini",
        run_local_tests=True,
        test_command=["pytest"],
        pythonpath_root=".",
        use_code_formatter=True,
        formatter_command=["ruff", "format"],
        fail_on_quality_error=True,
    )

    project = ProjectContext(
        root_path=Path(".").resolve(),
        pythonpath_root=".",
        source_roots=["core"],
        test_roots=["tests"],
        read_files=[
            "core/context.py",
            "core/work_order.py",
            "core/prompt.py",
            "core/checker.py",
        ],
        writable_files=[
            "core/project_context.py",
            "core/work_order.py",
            "core/context.py",
            "core/prompt.py",
            "core/validator.py",
        ],
        protected_files=[
            "core/executor.py",
        ],
    )

    work_order = WorkOrder(
        request_id="test_002",
        blueprint_name="python_registry_class",
        order_type=WorkOrderType.CREATE,
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
        read_files=project.read_files,
        writable_files=project.writable_files,
        invariants=[
            "Existing imports must remain valid.",
            "Only writable_files may be modified.",
            "Generated code must be importable with PYTHONPATH='.'.",
        ],
    )

    blueprint = registry.get(work_order.blueprint_name)

    context = ProductionContext(
        blueprint=blueprint,
        work_order=work_order,
        profile=profile,
        project=project,
    )

    line = ProductionLine(
        machines=[
            Validator(registry),
            ContextAssembler(),
            PromptBuilder(),
            ReviewBuilder(),
            Writer(),
            Executor(),
            OutputChecker(),
            OutputApplier(),
            Formatter(),
            TestRunner(),
        ]
    )

    context = line.run(context)

    print(f"LLM output written to: {context.response_path}")

    print("\n✅ APPLIED FILES:")
    for file_path in context.written_files:
        print(f"- {file_path}")

    print("✅ PRODUCTION LINE COMPLETED")

    print("\n📊 STEP RESULTS:")
    for step in context.step_results:
        status = "✅" if step.success else "❌"
        print(f"{status} {step.machine_name}: {step.message}")


if __name__ == "__main__":
    run()
