from core.blueprint import Blueprint


def build_python_pytest_unit_test_blueprint() -> Blueprint:
    return Blueprint(
        name="python_pytest_unit_test",
        component_type="unit_test",
        required_fields=[
            "target_name",
            "target_kind",
            "target_import_path",
            "target_path",
            "test_path",
            "responsibility",
            "definition_contract",
            "happy_path_behavior",
            "error_behavior",
        ],
        description=(
            "A reusable blueprint for generating a bounded pytest-based unit "
            "test module for an existing Python component."
        ),
        output_files=[
            "test_file",
        ],
        constraints=[
            "Generate exactly one pytest test module in the declared test file",
            "Do not generate production code",
            "Return only files declared in writable_files",
            "If the request is test-only, do not return the target_path "
            "as output",
            "Use pytest test functions, not unittest.TestCase",
            "Use clear, descriptive, behavior-oriented test function names",
            "Tests must target only the declared component",
            "Do not add external dependencies other than pytest and Python "
            "standard library modules",
            "Do not use vague placeholder descriptions in payload fields",
            "When the target behavior depends on structured text input, "
            "preserve the exact required text format in test fixtures",
            "Do not indent multiline sample content when line-start markers "
            "are part of the contract being tested",
            "When testing file-system behavior, create required directories "
            "before writing files or use pytest tmp_path",
            "Construct valid domain objects or minimal compatible test "
            "doubles for the target contract",
            "Enum-typed fields must use valid enum values, not "
            "placeholder strings",
            "When tests need sample content that mimics the LLM FILE block "
            "format, construct that content at runtime from string fragments",
            "Do not embed raw nested FILE block fixtures in a way that can "
            "be confused with the outer response format",
        ],
        quality_requirements=[
            "The test file must import pytest",
            "The test file must import the declared target component",
            "The generated tests must be specific to the declared component "
            "behavior",
            "At least 3 pytest test functions must be generated",
            "At least 1 happy path test must be generated",
            "At least 1 guard clause or error behavior test must be generated",
            "Tests must assert meaningful behavioral outcomes, not only object"
            "existence",
            "Tests must use realistic inputs derived from the component "
            "contract",
            "If the component parses structured text, the tests must provide "
            "format-valid sample content",
            "If the component interacts with the file system, the tests must "
            "handle paths and directories robustly",
            "The tests must avoid invalid placeholder values for typed fields",
            "Tests for parsers of FILE block responses must build sample "
            "response content safely without colliding with the outer "
            "generation format",
        ],
        default_invariants=[
            "Generated test code must be importable with PYTHONPATH='.'.",
            "Only declared writable files may be modified.",
            "Generated tests must follow Arrange-Act-Assert structure.",
            "Generated tests must remain bounded to the declared target "
            "component and task scope.",
        ],
    )
