from .blueprint import Blueprint
from .context_dependency import ContextDependencyResolution
from .target_analysis import TargetAnalysis
from .work_order import WorkOrder
from .work_order_draft_request import WorkOrderDraftRequest


class WorkOrderDraftBuilder:
    def build(
        self,
        *,
        request: WorkOrderDraftRequest,
        blueprint: Blueprint,
        analysis: TargetAnalysis,
        dependency_resolution: ContextDependencyResolution,
    ) -> WorkOrder:
        payload = self._build_payload(
            request=request,
            blueprint=blueprint,
            analysis=analysis,
        )

        writable_files = self._build_writable_files(
            request=request,
            blueprint=blueprint,
        )

        invariants = list(blueprint.default_invariants)
        acceptance_criteria = self._build_acceptance_criteria(
            blueprint=blueprint,
            request=request,
        )

        goal = self._build_goal(
            request=request,
            blueprint=blueprint,
        )

        read_files = list(dependency_resolution.required_read_files)
        for path in dependency_resolution.helpful_read_files:
            if path not in read_files:
                read_files.append(path)

        return WorkOrder(
            request_id=request.request_id,
            blueprint_name=request.blueprint_name,
            profile_name=request.profile_name,
            order_type=request.order_type,
            goal=goal,
            payload=payload,
            read_files=read_files,
            writable_files=writable_files,
            invariants=invariants,
            acceptance_criteria=acceptance_criteria,
        )

    def _build_goal(
        self,
        *,
        request: WorkOrderDraftRequest,
        blueprint: Blueprint,
    ) -> str:
        if blueprint.name == "python_pytest_unit_test":
            return (
                f"Generate a pytest-based unit test module for the "
                f"{request.target_name} component with focused behavioral coverage."
            )

        return f"Generate artifacts for blueprint {blueprint.name}."

    def _build_payload(
        self,
        *,
        request: WorkOrderDraftRequest,
        blueprint: Blueprint,
        analysis: TargetAnalysis,
    ) -> dict:
        if blueprint.name == "python_pytest_unit_test":
            return {
                "target_name": request.target_name,
                "target_kind": request.target_kind,
                "target_import_path": request.target_import_path,
                "target_path": request.target_path,
                "test_path": request.test_path or "",
                "responsibility": self._infer_responsibility(analysis),
                "definition_contract": self._infer_definition_contract(request, analysis),
                "happy_path_behavior": self._infer_happy_path(request, analysis),
                "error_behavior": self._infer_error_behavior(request, analysis),
            }

        raise ValueError(f"Unsupported blueprint for draft building: {blueprint.name}")

    def _build_writable_files(
        self,
        *,
        request: WorkOrderDraftRequest,
        blueprint: Blueprint,
    ) -> list[str]:
        if blueprint.name == "python_pytest_unit_test":
            if not request.test_path:
                raise ValueError("test_path is required for python_pytest_unit_test drafts.")
            return [request.test_path]

        return []

    def _build_acceptance_criteria(
        self,
        *,
        blueprint: Blueprint,
        request: WorkOrderDraftRequest,
    ) -> list[str]:
        criteria = list(blueprint.quality_requirements)

        if blueprint.name == "python_pytest_unit_test" and request.test_path:
            criteria.extend(
                [
                    "Return only files listed in writable_files.",
                    "Never return files from read_files.",
                    "Do not rewrite existing source files unless they are explicitly writable.",
                    f"For this request, exactly one file block must be returned: {request.test_path}",
                ]
            )

        return criteria

    def _infer_responsibility(self, analysis: TargetAnalysis) -> str:
        if analysis.public_methods:
            method_names = ", ".join(analysis.public_methods)
            return f"The component exposes the public methods: {method_names}."
        return "The component exposes a focused public interface."

    def _infer_definition_contract(
        self,
        request: WorkOrderDraftRequest,
        analysis: TargetAnalysis,
    ) -> str:
        if "run" in analysis.public_methods:
            return (
                f"The {request.target_name} exposes a public run(context) method "
                f"and returns the updated context."
            )
        return f"The {request.target_name} exposes a stable public API."

    def _infer_happy_path(
        self,
        request: WorkOrderDraftRequest,
        analysis: TargetAnalysis,
    ) -> str:
        if "run" in analysis.public_methods:
            return (
                f"When valid inputs are provided to {request.target_name}.run, "
                f"the operation completes successfully and returns the expected result."
            )
        return f"The main behavior of {request.target_name} succeeds for valid inputs."

    def _infer_error_behavior(
        self,
        request: WorkOrderDraftRequest,
        analysis: TargetAnalysis,
    ) -> str:
        return (
            f"{request.target_name} must fail deterministically when required inputs "
            f"or preconditions are missing."
        )
