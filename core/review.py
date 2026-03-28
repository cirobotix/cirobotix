from .context import ProductionContext


class ReviewBuilder:
    def run(self, context: ProductionContext) -> ProductionContext:
        payload = context.work_order.payload
        methods = "\n".join(f"- {method}" for method in payload["methods"])

        context.review_text = f"""# Review Summary

## Request ID
{context.work_order.request_id}

## Blueprint
{context.work_order.blueprint_name}

## Class Name
{payload["class_name"]}

## Source Path
{payload["target_path"]}

## Test Path
{payload["test_path"]}

## Responsibility
{payload["responsibility"]}

## Expected Methods
{methods}

## Behavioral Rules
- register(definition): {payload["definition_contract"]}
- get(name): {payload["get_behavior"]}
- list_names(): {payload["list_behavior"]}

## Review Checklist
- Does the source file contain exactly one class?
- Are all required methods present?
- Does register validate definition.name correctly?
- Does get raise KeyError for unknown names?
- Does list_names return sorted names?
- Are type hints included?
- Is a class docstring included?
- Is the pytest file at the exact requested path?
- Was unrelated functionality avoided?
"""
        return context
