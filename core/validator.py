from typing import Any

from .context import ProductionContext
from .work_order_type import WorkOrderType


class Validator:
    def __init__(self, registry) -> None:
        self.registry = registry

    def run(self, context: ProductionContext) -> ProductionContext:
        blueprint = self.registry.get(context.work_order.blueprint_name)

        self._validate_work_order_structure(context)
        self._validate_required_payload_fields(blueprint.required_fields, context.work_order.payload)
        self._validate_blueprint_payload(blueprint.name, context.work_order.payload)
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

    def _validate_blueprint_payload(
        self,
        blueprint_name: str,
        payload: dict[str, Any],
    ) -> None:
        if blueprint_name == "python_registry_class":
            self._validate_python_registry_class_payload(payload)
            return

        if blueprint_name == "python_pytest_unit_test":
            self._validate_python_pytest_unit_test_payload(payload)
            return

        raise ValueError(f"No payload validator defined for blueprint: {blueprint_name}")

    def _validate_python_registry_class_payload(self, payload: dict[str, Any]) -> None:
        class_name = payload["class_name"]
        target_path = payload["target_path"]
        methods = payload["methods"]
        responsibility = payload["responsibility"]
        test_path = payload["test_path"]
        definition_contract = payload["definition_contract"]
        get_behavior = payload["get_behavior"]
        list_behavior = payload["list_behavior"]

        if not isinstance(class_name, str) or not class_name.isidentifier():
            raise ValueError("class_name must be a valid Python identifier.")

        if not isinstance(target_path, str) or not target_path.endswith(".py"):
            raise ValueError("target_path must be a Python file path ending with '.py'.")

        if not isinstance(test_path, str) or not test_path.endswith(".py"):
            raise ValueError("test_path must be a Python file path ending with '.py'.")

        if not isinstance(responsibility, str) or len(responsibility.strip()) < 10:
            raise ValueError("responsibility must be a meaningful non-empty string.")

        if not isinstance(definition_contract, str) or len(definition_contract.strip()) < 10:
            raise ValueError("definition_contract must be a meaningful non-empty string.")

        if not isinstance(get_behavior, str) or len(get_behavior.strip()) < 10:
            raise ValueError("get_behavior must be a meaningful non-empty string.")

        if not isinstance(list_behavior, str) or len(list_behavior.strip()) < 10:
            raise ValueError("list_behavior must be a meaningful non-empty string.")

        if not isinstance(methods, list) or not methods:
            raise ValueError("methods must be a non-empty list.")

        for method in methods:
            if not isinstance(method, str) or not method.strip():
                raise ValueError("Each method entry must be a non-empty string.")

    def _validate_python_pytest_unit_test_payload(self, payload: dict[str, Any]) -> None:
        target_name = payload["target_name"]
        target_kind = payload["target_kind"]
        target_import_path = payload["target_import_path"]
        target_path = payload["target_path"]
        test_path = payload["test_path"]
        responsibility = payload["responsibility"]
        definition_contract = payload["definition_contract"]
        happy_path_behavior = payload["happy_path_behavior"]
        error_behavior = payload["error_behavior"]

        if not isinstance(target_name, str) or not target_name.isidentifier():
            raise ValueError("target_name must be a valid Python identifier.")

        if target_kind not in {"class", "function"}:
            raise ValueError("target_kind must be either 'class' or 'function'.")

        if not isinstance(target_import_path, str) or not target_import_path.strip():
            raise ValueError("target_import_path must be a non-empty string.")

        if "." not in target_import_path:
            raise ValueError(
                "target_import_path must look like a Python import path, e.g. 'core.applier'."
            )

        if not isinstance(target_path, str) or not target_path.endswith(".py"):
            raise ValueError("target_path must be a Python file path ending with '.py'.")

        if not isinstance(test_path, str) or not test_path.endswith(".py"):
            raise ValueError("test_path must be a Python file path ending with '.py'.")

        if "test_" not in test_path:
            raise ValueError("test_path must point to a pytest test module.")

        if not isinstance(responsibility, str) or len(responsibility.strip()) < 10:
            raise ValueError("responsibility must be a meaningful non-empty string.")

        if not isinstance(definition_contract, str) or len(definition_contract.strip()) < 10:
            raise ValueError("definition_contract must be a meaningful non-empty string.")

        if not isinstance(happy_path_behavior, str) or len(happy_path_behavior.strip()) < 10:
            raise ValueError("happy_path_behavior must be a meaningful non-empty string.")

        if not isinstance(error_behavior, str) or len(error_behavior.strip()) < 10:
            raise ValueError("error_behavior must be a meaningful non-empty string.")

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
