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
        description="A reusable blueprint for a bounded pytest-based unit test module for a Python component.",
        output_files=[
            "test_file",
        ],
        constraints=[
            "Generate exactly one pytest test module in the test file",
            "Do not generate production code",
            "Use pytest style test functions, not unittest.TestCase",
            "Use clear and descriptive test function names",
            "Do not add external dependencies other than pytest",
            "Tests must target only the declared component",
            "Generate exactly one pytest test module in the test file",
            "Do not generate production code",
            "Return only files declared in writable_files",
            "If the request is test-only, do not return target_path as output",
        ],
        quality_requirements=[
            "The test file must import pytest",
            "The test file must import the declared target component",
            "At least 3 pytest test functions must be generated",
            "At least 1 happy path test must be generated",
            "At least 1 guard clause or error behavior test must be generated",
        ],
        default_invariants=[
            "Generated test code must be importable with PYTHONPATH='.'.",
            "Only declared writable files may be modified.",
            "Generated tests must follow Arrange-Act-Assert structure.",
        ],
    )
