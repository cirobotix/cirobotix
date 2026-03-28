from core.context_assembler import ContextAssembler
from core.project_loader import ProjectLoader
from core.context import ProductionContext
from core.registry import Registry
from core.validator import Validator
from core.prompt import PromptBuilder
from core.review import ReviewBuilder
from core.work_order_loader import WorkOrderLoader
from core.writer import Writer
from core.executor import Executor
from core.checker import OutputChecker
from core.applier import OutputApplier
from core.test_runner import TestRunner
from core.production_line import ProductionLine
from core.formatter import Formatter
from core.profile_loader import ProfileLoader
from core.blueprints.catalog import register_blueprints


def run() -> None:

    project = ProjectLoader().load("config/projects/local_project.yaml")
    work_order = WorkOrderLoader().load("work_orders/test_002.yaml")
    profile = ProfileLoader().load(work_order.profile_name)

    registry = Registry()
    register_blueprints(registry)

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
