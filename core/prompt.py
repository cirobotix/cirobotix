from .context import ProductionContext


class PromptBuilder:
    def run(self, context: ProductionContext) -> ProductionContext:
        payload = context.work_order.payload
        project = context.project
        work_order = context.work_order

        methods = "\n".join(f"- {method}" for method in payload.get("methods", []))
        read_files = "\n".join(f"- {path}" for path in work_order.read_files) or "- none"
        writable_files = "\n".join(f"- {path}" for path in work_order.writable_files) or "- none"
        invariants = "\n".join(f"- {item}" for item in work_order.invariants) or "- none"

        context.prompt_text = f"""# Role
You are an experienced Python engineer working inside an existing codebase.

# Task
Generate exactly two files:
1. One Python source file
2. One pytest test file

# Work Order
- Request ID: {work_order.request_id}
- Blueprint: {work_order.blueprint_name}
- Order Type: {work_order.order_type.value}

# Project Context
- Project root: {project.root_path}
- Pythonpath root: {project.pythonpath_root}
- Source roots: {", ".join(project.source_roots)}
- Test roots: {", ".join(project.test_roots)}

# Existing Code Context
{context.assembled_context or "No additional context provided."}

# Read-Only Context Files
{read_files}

# Writable Files
{writable_files}

# Integration Invariants
{invariants}

# Source File Path
{payload.get("target_path", "")}

# Test File Path
{payload.get("test_path", "")}

# Class Name
{payload.get("class_name", "")}

# Responsibility
{payload.get("responsibility", "")}

# Required Methods
{methods}

# Behavioral Requirements
- register(definition): {payload.get("definition_contract", "")}
- get(name): {payload.get("get_behavior", "")}
- list_names(): {payload.get("list_behavior", "")}

# Constraints
- Generate exactly one Python class in the source file
- Do not create unrelated helper classes
- Only modify files listed under Writable Files
- Preserve compatibility with the existing import structure
- Use type hints
- Include a class docstring
- The generated class MUST contain a class-level docstring
- The docstring MUST be placed directly below the class declaration
- Use triple quotes for the class docstring
- The absence of a class docstring is considered a failure
- Keep the implementation minimal and readable
- Do not add external dependencies
- Use pytest for tests
- All modules must be importable relative to the configured Pythonpath root

# Import Requirement
- All referenced type hints must be properly imported
- The source file must be valid Python and importable
- Do not use Any unless it is explicitly imported from typing
Use this exact import in the test file:
from core.generated_registry import ArtifactRegistry

# Test File Requirement
The test file must import the pytest library.
The test file must import the generated class using this exact import:
from core.generated_registry import ArtifactRegistry

# Final Verification Before Output
Before returning the code, verify that:
- The source file contains exactly one class named {payload.get("class_name", "")}
- The class contains a docstring directly below the class declaration
- The required methods are present
- The test file imports pytest
- The test file imports the generated class with the exact required import
- Exactly two files are returned
- The output strictly follows the requested format

# Output Format
Return only code.
Use this exact structure:

### FILE: {payload.get("target_path", "")}
```python
# source code here
FILE: {payload.get("test_path", "")}
# test code here
"""
        return context
