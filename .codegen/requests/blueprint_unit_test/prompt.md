# Role
You are an experienced Python engineer working inside an existing codebase.

# Task
Generate exactly the files declared in Writable Files.
Do not return any additional files.
Do not return read-only files.
Do not include explanations outside the requested file blocks.

# Work Order
- Request ID: blueprint_unit_test
- Blueprint: python_pytest_unit_test
- Component Type: unit_test
- Order Type: create
- Goal: Generate a pytest-based unit test module for the Blueprint dataclass with focused structural and behavioral coverage.

# Project Context
- Project root: /Users/jensbekersch/PycharmProjects/ci_robotix
- Pythonpath root: .
- Source roots: core
- Test roots: tests

# Existing Code Context
## FILE: core/blueprint.py
```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Blueprint:
    name: str
    component_type: str
    required_fields: list[str]

    description: str = ""
    output_files: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    quality_requirements: list[str] = field(default_factory=list)
    default_invariants: list[str] = field(default_factory=list)

```

# Read-Only Context Files
- core/blueprint.py

# Writable Files
- tests/core/test_blueprint.py

# Blueprint Constraints
- Generate exactly one pytest test module in the test file
- Do not generate production code
- Use pytest style test functions, not unittest.TestCase
- Use clear and descriptive test function names
- Do not add external dependencies other than pytest
- Tests must target only the declared component
- Generate exactly one pytest test module in the test file
- Do not generate production code
- Return only files declared in writable_files
- If the request is test-only, do not return target_path as output

# Quality Requirements
- The test file must import pytest
- The test file must import the declared target component
- At least 3 pytest test functions must be generated
- At least 1 happy path test must be generated
- At least 1 guard clause or error behavior test must be generated

# Integration Invariants
- Generated test code must be importable with PYTHONPATH='.'.
- Only declared writable files may be returned.
- The generated tests must target only the declared component.
- The generated tests must follow Arrange-Act-Assert structure.

# Acceptance Criteria
- The test file imports pytest.
- The test file imports Blueprint from core.blueprint.
- The tests import all necessary libraries
- At least 3 pytest test functions are generated.
- The tests cover construction with required fields.
- The tests cover default values of optional fields.
- The tests cover immutability of the frozen dataclass.
- The tests verify that list defaults are independent between instances.
- Return only files listed in writable_files.
- Never return files from read_files.
- Do not rewrite existing source files unless they are explicitly writable.
- {'For this request, exactly one file block must be returned': 'tests/core/test_blueprint.py'}

# Payload
- target_name: Blueprint
- target_kind: class
- target_import_path: core.blueprint
- target_path: core/blueprint.py
- test_path: tests/core/test_blueprint.py
- responsibility: Represent a reusable immutable blueprint definition for code generation requests.
- definition_contract: The Blueprint is a frozen dataclass that stores required blueprint metadata and optional configuration lists.
- happy_path_behavior: The Blueprint dataclass stores required and optional values correctly and exposes them unchanged after construction.
- error_behavior: The Blueprint constructor fails when required fields are missing, and attribute mutation is rejected after instantiation because the dataclass is frozen.

# Test-Only Rule
- This is a test-only request.
- Do not return production source files.
- Do not return this read-only target file as output: core/blueprint.py

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

### FILE: tests/core/test_blueprint.py
```python
# code here
```
