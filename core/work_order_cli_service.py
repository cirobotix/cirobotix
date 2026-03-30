from pathlib import Path

from .applier import OutputApplier
from .blueprints.catalog import register_blueprints
from .checker import OutputChecker
from .context import ProductionContext
from .context_assembler import ContextAssembler
from .context_dependency_resolver import ContextDependencyResolver
from .executor import Executor
from .formatter import Formatter
from .production_line import ProductionLine
from .profile_loader import ProfileLoader
from .project_loader import ProjectLoader
from .prompt import PromptBuilder
from .python_class_discovery import PythonClassDiscovery
from .registry import Registry
from .request_id_builder import RequestIdBuilder
from .review import ReviewBuilder
from .target_inspector import TargetInspector
from .target_path_helper import TargetPathHelper
from .test_runner import TestRunner
from .validator import Validator
from .work_order_cli_review_writer import WorkOrderCliReviewWriter
from .work_order_cli_runtime_writer import WorkOrderCliRuntimeWriter
from .work_order_draft_builder import WorkOrderDraftBuilder
from .work_order_draft_request import WorkOrderDraftRequest
from .work_order_loader import WorkOrderLoader
from .work_order_type import WorkOrderType
from .work_order_writer import WorkOrderWriter


class WorkOrderCliService:
    def __init__(self) -> None:
        self.project_loader = ProjectLoader()
        self.profile_loader = ProfileLoader()
        self.work_order_loader = WorkOrderLoader()
        self.target_helper = TargetPathHelper()
        self.class_discovery = PythonClassDiscovery()
        self.target_inspector = TargetInspector()
        self.dependency_resolver = ContextDependencyResolver()
        self.request_id_builder = RequestIdBuilder()
        self.draft_builder = WorkOrderDraftBuilder()
        self.work_order_writer = WorkOrderWriter()
        self.review_writer = WorkOrderCliReviewWriter()

    def create_registry(self) -> Registry:
        registry = Registry()
        register_blueprints(registry)
        return registry

    def create_draft(
        self,
        *,
        blueprint_name: str,
        target_path: str,
        project_config_path: str = "config/projects/local_project.yaml",
        profile_name: str = "default",
    ) -> Path:
        registry = self.create_registry()
        blueprint = registry.get(blueprint_name)
        project = self.project_loader.load(project_config_path)

        resolved_target_path = project.resolve(target_path)
        if not resolved_target_path.exists():
            raise FileNotFoundError(f"Target file not found: {target_path}")

        target_import_path = self.target_helper.to_import_path(target_path)
        target_name = self.class_discovery.find_primary_class_name(resolved_target_path)
        test_path = self.target_helper.to_test_path(target_path)
        request_id = self.request_id_builder.build(blueprint_name, target_path)

        draft_request = WorkOrderDraftRequest(
            request_id=request_id,
            blueprint_name=blueprint_name,
            profile_name=profile_name,
            order_type=WorkOrderType.CREATE,
            target_name=target_name,
            target_kind="class",
            target_import_path=target_import_path,
            target_path=target_path,
            test_path=test_path,
        )

        analysis = self.target_inspector.inspect(
            project=project,
            target_path=target_path,
            target_import_path=target_import_path,
            target_kind="class",
            target_name=target_name,
        )

        dependency_resolution = self.dependency_resolver.resolve(
            project=project,
            analysis=analysis,
        )

        work_order = self.draft_builder.build(
            request=draft_request,
            blueprint=blueprint,
            analysis=analysis,
            dependency_resolution=dependency_resolution,
        )

        base_dir = Path(".codegen") / "requests" / request_id
        self.work_order_writer.write(work_order, base_dir)
        self.review_writer.write(work_order, base_dir)

        return base_dir / "task.yaml"

    def generate(
        self,
        *,
        work_order_path: str,
        project_config_path: str = "config/projects/local_project.yaml",
    ) -> ProductionContext:
        work_order = self.work_order_loader.load(work_order_path)
        project = self.project_loader.load(project_config_path)
        profile = self.profile_loader.load(work_order.profile_name)

        registry = self.create_registry()
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
                WorkOrderCliRuntimeWriter(),
                Executor(),
                OutputChecker(),
                OutputApplier(),
                Formatter(),
                TestRunner(),
            ]
        )

        return line.run(context)
