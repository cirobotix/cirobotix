from typing import Any

from .context import ProductionContext
from .registry import Registry
from .work_order_type import WorkOrderType


class Validator:
    def __init__(self, registry: Registry) -> None:
        self.registry = registry

    def run(self, context: ProductionContext) -> ProductionContext:
        blueprint = self.registry.get(context.work_order.blueprint_name)

        self._validate_work_order_structure(context)
        self._validate_required_payload_fields(
            blueprint.required_fields,
            context.work_order.payload,
        )
        self._validate_project_context(context)

        return context

    def _validate_work_order_structure(self, context: ProductionContext) -> None:
        work_order = context.work_order

        if not isinstance(work_order.request_id, str) or not work_order.request_id.strip():
            raise ValueError("request_id must be a non-empty string.")

        if not isinstance(work_order.blueprint_name, str) or not work_order.blueprint_name.strip():
            raise ValueError("blueprint_name must be a non-empty string.")

        if not isinstance(work_order.profile_name, str) or not work_order.profile_name.strip():
            raise ValueError("profile_name must be a non-empty string.")

        if not isinstance(work_order.goal, str) or not work_order.goal.strip():
            raise ValueError("goal must be a non-empty string.")

        if not isinstance(work_order.read_files, list):
            raise ValueError("read_files must be a list.")

        if not isinstance(work_order.writable_files, list):
            raise ValueError("writable_files must be a list.")

        if not isinstance(work_order.invariants, list):
            raise ValueError("invariants must be a list.")

        if not isinstance(work_order.acceptance_criteria, list):
            raise ValueError("acceptance_criteria must be a list.")

        if not isinstance(work_order.payload, dict):
            raise ValueError("payload must be a dictionary.")

    def _validate_required_payload_fields(
        self,
        required_fields: list[str],
        payload: dict[str, Any],
    ) -> None:
        missing: list[str] = []

        for field_name in required_fields:
            value = payload.get(field_name)
            if value is None:
                missing.append(field_name)
            elif isinstance(value, str) and not value.strip():
                missing.append(field_name)

        if missing:
            raise ValueError(f"Missing required fields: {missing}")

    def _validate_project_context(self, context: ProductionContext) -> None:
        project = context.project
        work_order = context.work_order

        if not project.root_path.exists():
            raise ValueError("project.root_path does not exist.")

        if work_order.order_type == WorkOrderType.MODIFY and not work_order.writable_files:
            raise ValueError("modify work orders must define writable_files.")

        for relative_path in work_order.read_files + work_order.writable_files:
            if not isinstance(relative_path, str) or not relative_path.strip():
                raise ValueError("All file paths must be non-empty strings.")

        for relative_path in work_order.read_files:
            if not project.resolve(relative_path).exists():
                raise ValueError(f"Read file does not exist: {relative_path}")

        for relative_path in work_order.writable_files:
            if relative_path in project.protected_files:
                raise ValueError(f"Protected file cannot be writable: {relative_path}")
