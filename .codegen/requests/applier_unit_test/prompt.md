# Role
You are an experienced Python engineer working inside an existing codebase.

# Task
Generate exactly the files declared in Writable Files.
Do not return any additional files.
Do not return read-only files.
Do not include explanations outside the requested file blocks.

# Work Order
- Request ID: applier_unit_test
- Blueprint: python_pytest_unit_test
- Component Type: unit_test
- Order Type: create
- Goal: Generate a pytest-based unit test module for the Applier component with full behavioral coverage.

# Project Context
- Project root: /Users/jensbekersch/PycharmProjects/ci_robotix
- Pythonpath root: .
- Source roots: core
- Test roots: tests

# Existing Code Context
## FILE: core/applier.py
```python
import re
from pathlib import Path

from .context import ProductionContext


class OutputApplier:
    def run(self, context: ProductionContext) -> ProductionContext:
        base = Path(".codegen") / "requests" / context.work_order.request_id
        response_path = base / "response.md"

        if not response_path.exists():
            raise FileNotFoundError("response.md not found")

        content = response_path.read_text(encoding="utf-8")
        files = self._extract_files(content)

        written_files: list[Path] = []

        for relative_path, code in files.items():
            target = Path(relative_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code.rstrip() + "\n", encoding="utf-8")
            written_files.append(target)

        context.written_files = written_files
        return context

    def _extract_files(self, content: str) -> dict[str, str]:
        pattern = (
            r"(?ms)^### FILE:\s*(.+?)\n"
            r"^```[a-zA-Z0-9_-]*\n"
            r"(.*?)"
            r"^```[ \t]*$"
        )
        matches = re.findall(pattern, content)

        files: dict[str, str] = {}
        for path, code in matches:
            files[path.strip()] = code.strip()

        if not files:
            raise ValueError("No file blocks found in response")

        return files

```

## FILE: core/context.py
```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .blueprint import Blueprint
from .profile import ProductionProfile
from .project_context import ProjectContext
from .result import StepResult
from .work_order import WorkOrder


@dataclass
class ProductionContext:
    blueprint: Blueprint
    work_order: WorkOrder
    profile: ProductionProfile
    project: ProjectContext

    base_dir: Optional[Path] = None
    prompt_text: Optional[str] = None
    review_text: Optional[str] = None
    response_path: Optional[Path] = None
    assembled_context: Optional[str] = None

    written_files: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    step_results: list[StepResult] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_step_result(self, result: StepResult) -> None:
        self.step_results.append(result)

```

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

## FILE: core/profile.py
```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProductionProfile:
    llm_model: str = "gpt-4o-mini"
    run_local_tests: bool = True
    test_command: list[str] = field(default_factory=lambda: ["pytest"])
    pythonpath_root: str = "."
    use_code_formatter: bool = False
    formatter_command: list[str] = field(default_factory=list)
    fail_on_quality_error: bool = True

```

## FILE: core/project_context.py
```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProjectContext:
    root_path: Path
    pythonpath_root: str = "."
    source_roots: list[str] = field(default_factory=list)
    test_roots: list[str] = field(default_factory=list)
    protected_files: list[str] = field(default_factory=list)

    def resolve(self, relative_path: str) -> Path:
        return self.root_path / relative_path

```

## FILE: core/result.py
```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepResult:
    machine_name: str
    success: bool
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

```

## FILE: core/work_order.py
```python
from dataclasses import asdict, dataclass, field
from typing import Any

from .work_order_type import WorkOrderType


@dataclass(frozen=True)
class WorkOrder:
    request_id: str
    blueprint_name: str
    profile_name: str
    order_type: WorkOrderType
    goal: str
    payload: dict[str, Any]

    read_files: list[str] = field(default_factory=list)
    writable_files: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

```

# Read-Only Context Files
- core/applier.py
- core/context.py
- core/blueprint.py
- core/profile.py
- core/project_context.py
- core/result.py
- core/work_order.py

# Writable Files
- tests/core/test_applier.py

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
- The test file imports Applier from core.applier.
- At least 3 pytest test functions are generated.
- Happy path behavior is covered.
- Guard clauses and edge cases are covered.
- The generated tests are designed to achieve 100 percent line coverage for the Applier class.
- return **only** files listed in `writable_files`
- never return files from `read_files`
- do not rewrite existing source files unless they are explicitly writable
- {'For this request, exactly one file block must be returned': 'tests/core/test_applier.py'}
- Create all needed fixtures

# Payload
- target_name: Applier
- target_kind: class
- target_import_path: core.applier
- target_path: core/applier.py
- test_path: tests/core/test_applier.py
- responsibility: Apply generated output artifacts to the declared writable target files.
- definition_contract: The Applier exposes a public run(context) method that writes only declared output artifacts to allowed writable files and returns the updated context.
- happy_path_behavior: When valid generated artifacts are present in the context and all target paths are declared writable, the Applier writes the files and returns the updated context.
- error_behavior: The Applier must fail deterministically when required context data is missing, when no writable target is available, or when an artifact targets a path outside the declared writable files.

# Test-Only Rule
- This is a test-only request.
- Do not return production source files.
- Do not return this read-only target file as output: core/applier.py

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

### FILE: tests/core/test_applier.py
```python
# code here
```
