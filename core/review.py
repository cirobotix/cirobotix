from .context import ProductionContext


class ReviewBuilder:
    def run(self, context: ProductionContext) -> ProductionContext:
        work_order = context.work_order
        payload = work_order.payload

        payload_lines = "\n".join(
            f"- {key}: {self._format_value(value)}" for key, value in payload.items()
        )

        acceptance_lines = "\n".join(
            f"- {criterion}" for criterion in work_order.acceptance_criteria
        )

        invariant_lines = "\n".join(
            f"- {invariant}" for invariant in work_order.invariants
        )

        read_file_lines = "\n".join(f"- {path}" for path in work_order.read_files)
        writable_file_lines = "\n".join(f"- {path}" for path in work_order.writable_files)

        context.review_text = f"""# Review Summary

## Request ID
{work_order.request_id}

## Blueprint
{work_order.blueprint_name}

## Goal
{work_order.goal}

## Read Files
{read_file_lines or "- None"}

## Writable Files
{writable_file_lines or "- None"}

## Invariants
{invariant_lines or "- None"}

## Acceptance Criteria
{acceptance_lines or "- None"}

## Payload
{payload_lines or "- None"}

## Review Checklist
- Does the result satisfy the declared goal?
- Are only declared writable files modified?
- Are all acceptance criteria addressed?
- Are all invariants respected?
- Does the output match the selected blueprint?
"""

        return context

    def _format_value(self, value) -> str:
        if isinstance(value, list):
            if not value:
                return "[]"
            return "[" + ", ".join(str(item) for item in value) + "]"
        return str(value)
