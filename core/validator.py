from typing import Any

from .context import ProductionContext


class Validator:
    def __init__(self, registry) -> None:
        self.registry = registry

    def run(self, context: ProductionContext) -> ProductionContext:
        blueprint = self.registry.get(context.work_order.blueprint_name)

        missing: list[str] = []
        for field_name in blueprint.required_fields:
            value = context.work_order.payload.get(field_name)
            if value is None:
                missing.append(field_name)
            elif isinstance(value, str) and not value.strip():
                missing.append(field_name)

        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        self._validate_payload(context.work_order.payload)
        return context

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        class_name = payload["class_name"]
        target_path = payload["target_path"]
        methods = payload["methods"]
        responsibility = payload["responsibility"]
        test_path = payload["test_path"]
        definition_contract = payload["definition_contract"]
        get_behavior = payload["get_behavior"]
        list_behavior = payload["list_behavior"]

        if not isinstance(test_path, str) or not test_path.endswith(".py"):
            raise ValueError("test_path must be a Python file path ending with '.py'.")

        if not isinstance(definition_contract, str) or len(definition_contract.strip()) < 10:
            raise ValueError("definition_contract must be a meaningful non-empty string.")

        if not isinstance(get_behavior, str) or len(get_behavior.strip()) < 10:
            raise ValueError("get_behavior must be a meaningful non-empty string.")

        if not isinstance(list_behavior, str) or len(list_behavior.strip()) < 10:
            raise ValueError("list_behavior must be a meaningful non-empty string.")

        if not isinstance(class_name, str) or not class_name.isidentifier():
            raise ValueError("class_name must be a valid Python identifier.")

        if not isinstance(target_path, str) or not target_path.endswith(".py"):
            raise ValueError("target_path must be a Python file path ending with '.py'.")

        if not isinstance(responsibility, str) or len(responsibility.strip()) < 10:
            raise ValueError("responsibility must be a meaningful non-empty string.")

        if not isinstance(methods, list) or not methods:
            raise ValueError("methods must be a non-empty list.")

        for method in methods:
            if not isinstance(method, str) or not method.strip():
                raise ValueError("Each method entry must be a non-empty string.")
