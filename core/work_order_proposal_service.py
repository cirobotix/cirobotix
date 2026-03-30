import shutil
from pathlib import Path

from .atomic_task_loader import AtomicTaskLoader
from .blueprints.catalog import register_blueprints
from .context_assembler import ContextAssembler
from .context_dependency_resolver import ContextDependencyResolver
from .profile_loader import ProfileLoader
from .project_loader import ProjectLoader
from .registry import Registry
from .target_inspector import TargetInspector
from .work_order import WorkOrder
from .work_order_proposal_executor import WorkOrderProposalExecutor
from .work_order_proposal_prompt_builder import WorkOrderProposalPromptBuilder
from .work_order_proposal_writer import WorkOrderProposalWriter
from .work_order_type import WorkOrderType
from .context import ProductionContext
from .profile import ProductionProfile
from .review import ReviewBuilder
from .validator import Validator
from .work_order_loader import WorkOrderLoader


class WorkOrderProposalService:
    def __init__(self) -> None:
        self.atomic_task_loader = AtomicTaskLoader()
        self.project_loader = ProjectLoader()
        self.profile_loader = ProfileLoader()
        self.prompt_builder = WorkOrderProposalPromptBuilder()
        self.executor = WorkOrderProposalExecutor()
        self.writer = WorkOrderProposalWriter()
        self.target_inspector = TargetInspector()
        self.dependency_resolver = ContextDependencyResolver()
        self.context_assembler = ContextAssembler()
        self.work_order_loader = WorkOrderLoader()

    def create_registry(self) -> Registry:
        registry = Registry()
        register_blueprints(registry)
        return registry

    def create_ai_proposal(
        self,
        *,
        task_path: str,
        profile_name: str = "default",
        project_config_path: str = "config/projects/local_project.yaml",
    ) -> str:
        task = self.atomic_task_loader.load(task_path)
        registry = self.create_registry()
        blueprint = registry.get(task.blueprint_name)
        project = self.project_loader.load(project_config_path)
        profile = self.profile_loader.load(profile_name)

        target_path = task.inputs["target_path"]
        target_import_path = task.inputs["target_import_path"]
        target_kind = task.inputs["target_kind"]
        target_name = task.inputs["target_name"]
        test_path = task.inputs["test_path"]

        analysis = self.target_inspector.inspect(
            project=project,
            target_path=target_path,
            target_import_path=target_import_path,
            target_kind=target_kind,
            target_name=target_name,
        )

        dependency_resolution = self.dependency_resolver.resolve(
            project=project,
            analysis=analysis,
        )

        suggested_read_files = list(dependency_resolution.required_read_files)
        for path in dependency_resolution.helpful_read_files:
            if path not in suggested_read_files:
                suggested_read_files.append(path)

        suggested_writable_files = [test_path]

        proposal_stub = WorkOrder(
            request_id=task.task_id,
            blueprint_name=task.blueprint_name,
            profile_name=profile_name,
            order_type=WorkOrderType.CREATE,
            goal=task.title,
            payload=dict(task.inputs),
            read_files=suggested_read_files,
            writable_files=suggested_writable_files,
            invariants=list(blueprint.default_invariants),
            acceptance_criteria=list(task.acceptance_criteria),
        )

        context = ProductionContext(
            blueprint=blueprint,
            work_order=proposal_stub,
            profile=profile,
            project=project,
        )

        context = self.context_assembler.run(context)

        prompt = self.prompt_builder.build(
            blueprint=blueprint,
            task=task,
            assembled_context=context.assembled_context or "",
            suggested_read_files=suggested_read_files,
            suggested_writable_files=suggested_writable_files,
        )

        proposal_text = self.executor.generate(
            model=profile.llm_model,
            prompt=prompt,
        )

        proposal_path = self.writer.write(
            request_id=task.task_id,
            proposal_text=proposal_text,
        )

        return str(proposal_path)

    def promote_proposal(
        self,
        *,
        proposal_path: str,
        project_config_path: str = "config/projects/local_project.yaml",
    ) -> str:
        registry = self.create_registry()
        project = self.project_loader.load(project_config_path)

        work_order = self.work_order_loader.load(proposal_path)
        blueprint = registry.get(work_order.blueprint_name)

        context = ProductionContext(
            blueprint=blueprint,
            work_order=work_order,
            profile=ProductionProfile(),
            project=project,
        )

        Validator(registry).run(context)

        proposal_file = Path(proposal_path)
        task_path = proposal_file.parent / "task.yaml"
        shutil.copyfile(proposal_file, task_path)

        review_context = ReviewBuilder().run(context)
        review_path = proposal_file.parent / "review.md"
        review_path.write_text(review_context.review_text or "", encoding="utf-8")

        return str(task_path)