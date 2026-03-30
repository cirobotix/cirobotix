from .context import ProductionContext


class PromptBuilder:
    def run(self, context: ProductionContext) -> ProductionContext:
        blueprint = context.blueprint
        payload = context.work_order.payload
        project = context.project
        work_order = context.work_order

        read_files = "\n".join(f"- {path}" for path in work_order.read_files) or "- none"
        writable_files = "\n".join(f"- {path}" for path in work_order.writable_files) or "- none"
        invariants = "\n".join(f"- {item}" for item in work_order.invariants) or "- none"
        acceptance_criteria = (
            "\n".join(f"- {item}" for item in work_order.acceptance_criteria) or "- none"
        )
        constraints = "\n".join(f"- {item}" for item in blueprint.constraints) or "- none"
        quality_requirements = (
            "\n".join(f"- {item}" for item in blueprint.quality_requirements) or "- none"
        )
        payload_lines = "\n".join(
            f"- {key}: {self._format_value(value)}" for key, value in payload.items()
        ) or "- none"

        output_file_blocks = "\n\n".join(
            f"""### FILE: {path}
```python
# code here
```"""
            for path in work_order.writable_files
        )

        test_only_instruction = ""
        if (
            blueprint.component_type == "unit_test"
            and "target_path" in payload
            and payload["target_path"] not in work_order.writable_files
        ):
            test_only_instruction = (
                "\n# Test-Only Rule\n"
                "- This is a test-only request.\n"
                "- Do not return production source files.\n"
                f"- Do not return this read-only target file as output: {payload['target_path']}\n"
            )

        context.prompt_text = f"""# Role
You are an experienced Python engineer working inside an existing codebase.

# Task
Generate exactly the files declared in Writable Files.
Do not return any additional files.
Do not return read-only files.
Do not include explanations outside the requested file blocks.

# Work Order
- Request ID: {work_order.request_id}
- Blueprint: {work_order.blueprint_name}
- Component Type: {blueprint.component_type}
- Order Type: {work_order.order_type.value}
- Goal: {work_order.goal}

# Project Context
- Project root: {project.root_path}
- Pythonpath root: {project.pythonpath_root}
- Source roots: {", ".join(project.source_roots) or "- none"}
- Test roots: {", ".join(project.test_roots) or "- none"}

# Existing Code Context
{context.assembled_context or "No additional context provided."}

# Read-Only Context Files
{read_files}

# Writable Files
{writable_files}

# Blueprint Constraints
{constraints}

# Quality Requirements
{quality_requirements}

# Integration Invariants
{invariants}

# Acceptance Criteria
{acceptance_criteria}

# Payload
{payload_lines}
{test_only_instruction}
# Output Rules
- Return output blocks only for files listed under Writable Files.
- Every writable file must be returned exactly once.
- Do not return files from Read-Only Context Files.
- Do not modify or return protected or undeclared files.
- All generated Python modules must be importable relative to the configured Pythonpath root.
- Use valid Python syntax.
- Preserve compatibility with the existing import structure.
- Do not add external dependencies unless explicitly required.
- If the request is test-only, return only the test file blocks.

# Final Verification Before Output
Before returning the result, verify that:
- Only writable files are returned.
- Every writable file has exactly one output block.
- No read-only file is returned as output.
- The result satisfies the goal, constraints, invariants, and acceptance criteria.
- The output strictly follows the requested format.

# Output Format
Return only code using this exact structure:

{output_file_blocks}
"""
        return context

    def _format_value(self, value) -> str:
        if isinstance(value, list):
            if not value:
                return "[]"
            return "[" + ", ".join(str(item) for item in value) + "]"
        return str(value)
