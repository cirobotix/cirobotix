from core.blueprint import Blueprint


def build_python_data_model_blueprint() -> Blueprint:
    return Blueprint(
        name="python_data_model",
        component_type="data_model",
        required_fields=[
            "class_name",
            "target_path",
            "test_path",
            "responsibility",
            "fields",
        ],
        description="A reusable blueprint for a Python data model component.",
        output_files=[
            "source_file",
            "test_file",
        ],
        constraints=[
            "Generate exactly one Python class in the source file",
            "Use type hints",
            "Include a class docstring",
            "Keep the model minimal and readable",
            "Do not add external dependencies",
        ],
        quality_requirements=[
            "The test file must import pytest",
            "The test file must validate model construction and field behavior",
        ],
        default_invariants=[
            "Generated code must remain importable.",
            "Only declared writable files may be modified.",
        ],
    )
