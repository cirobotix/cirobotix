from core.models.blueprint import Blueprint


def build_python_registry_class_blueprint() -> Blueprint:
    return Blueprint(
        name="python_registry_class",
        component_type="registry",
        required_fields=[
            "class_name",
            "target_path",
            "test_path",
            "methods",
            "responsibility",
            "definition_contract",
            "get_behavior",
            "list_behavior",
        ],
        description="A reusable blueprint for a bounded Python registry component.",
        output_files=[
            "source_file",
            "test_file",
        ],
        constraints=[
            "Generate exactly one Python class in the source file",
            "Do not create unrelated helper classes",
            "Use type hints",
            "Include a class docstring",
            "Do not add external dependencies",
        ],
        quality_requirements=[
            "The test file must import pytest",
            "The test file must import the generated registry class",
            "At least 3 pytest test functions must be generated",
        ],
        default_invariants=[
            "Generated code must be importable with PYTHONPATH='.'.",
            "Only declared writable files may be modified.",
        ],
    )
