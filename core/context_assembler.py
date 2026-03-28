from .context import ProductionContext


class ContextAssembler:
    def __init__(self, max_chars_per_file: int = 4000) -> None:
        self.max_chars_per_file = max_chars_per_file

    def run(self, context: ProductionContext) -> ProductionContext:
        project = context.project
        work_order = context.work_order

        assembled_context_parts: list[str] = []

        for relative_path in work_order.read_files:
            file_path = project.resolve(relative_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Context file not found: {relative_path}")

            content = file_path.read_text(encoding="utf-8")

            truncated = self._truncate(content)

            assembled_context_parts.append(
                f"""## FILE: {relative_path}
```python
{truncated}
```"""
            )

        context.assembled_context = "\n\n".join(assembled_context_parts)
        return context

    def _truncate(self, content: str) -> str:
        if len(content) <= self.max_chars_per_file:
            return content
        return content[: self.max_chars_per_file] + "\n# ... truncated ..."
