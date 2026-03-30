import pytest

from core.applier import OutputApplier
from core.blueprint import Blueprint
from core.context import ProductionContext
from core.profile import ProductionProfile
from core.project_context import ProjectContext
from core.work_order import WorkOrder


@pytest.fixture
def valid_context():
    blueprint = Blueprint(name="test_blueprint", component_type="test", required_fields=[])
    work_order = WorkOrder(
        request_id="applier_unit_test",
        blueprint_name="test_blueprint",
        profile_name="test_profile",
        order_type="create",
        goal="test",
        payload={},
    )
    profile = ProductionProfile()
    project_context = ProjectContext(root_path=".", source_roots=[], test_roots=[])

    return ProductionContext(
        blueprint=blueprint, work_order=work_order, profile=profile, project=project_context
    )


def test_output_applier_happy_path(valid_context, mocker):
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch(
        "pathlib.Path.read_text",
        return_value="### FILE: output.txt\n```python\nprint('Hello World')\n```",
    )

    applier = OutputApplier()
    updated_context = applier.run(valid_context)

    assert len(updated_context.written_files) == 1
    assert str(updated_context.written_files[0]) == "output.txt"


def test_output_applier_file_not_found(valid_context, mocker):
    mocker.patch("pathlib.Path.exists", return_value=False)

    applier = OutputApplier()

    with pytest.raises(FileNotFoundError, match="response.md not found"):
        applier.run(valid_context)


def test_output_applier_no_files_extracted(valid_context, mocker):
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value="No files here")

    applier = OutputApplier()

    with pytest.raises(ValueError, match="No file blocks found in response"):
        applier.run(valid_context)
