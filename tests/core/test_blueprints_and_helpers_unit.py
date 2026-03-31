from pathlib import Path

import pytest

from core.blueprints.python_pytest_unit_test import build_python_pytest_unit_test_blueprint
from core.blueprints.python_registry_class import build_python_registry_class_blueprint
from core.helpers.python_class_discovery import PythonClassDiscovery
from core.helpers.request_id_builder import RequestIdBuilder
from core.helpers import request_id_builder as request_id_builder_module
from core.helpers.target_path_helper import TargetPathHelper


def test_build_python_pytest_unit_test_blueprint_has_expected_shape():
    blueprint = build_python_pytest_unit_test_blueprint()

    assert blueprint.name == "python_pytest_unit_test"
    assert blueprint.component_type == "unit_test"
    assert "target_name" in blueprint.required_fields
    assert blueprint.output_files == ["test_file"]
    assert any("pytest" in item for item in blueprint.quality_requirements)
    assert len(blueprint.constraints) > 5
    assert len(blueprint.default_invariants) == 4


def test_build_python_registry_class_blueprint_has_expected_shape():
    blueprint = build_python_registry_class_blueprint()

    assert blueprint.name == "python_registry_class"
    assert blueprint.component_type == "registry"
    assert "class_name" in blueprint.required_fields
    assert blueprint.output_files == ["source_file", "test_file"]
    assert "Use type hints" in blueprint.constraints
    assert len(blueprint.default_invariants) == 2


def test_python_class_discovery_returns_first_public_class(tmp_path: Path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(
        """
class _Hidden:
    pass

class PublicOne:
    pass

class PublicTwo:
    pass
""".strip(),
        encoding="utf-8",
    )

    assert PythonClassDiscovery().find_primary_class_name(file_path) == "PublicOne"


def test_python_class_discovery_raises_when_no_public_class(tmp_path: Path):
    file_path = tmp_path / "sample.py"
    file_path.write_text("class _OnlyPrivate:\n    pass\n", encoding="utf-8")

    with pytest.raises(ValueError, match="No public class found"):
        PythonClassDiscovery().find_primary_class_name(file_path)


def test_request_id_builder_normalizes_stem_and_uses_timestamp(monkeypatch):
    class FakeNow:
        def strftime(self, fmt: str) -> str:
            assert fmt == "%Y%m%d_%H%M%S"
            return "20260331_123456"

    class FakeDateTime:
        @classmethod
        def now(cls):
            return FakeNow()

    monkeypatch.setattr(request_id_builder_module, "datetime", FakeDateTime)

    result = RequestIdBuilder().build("bp", "src/My- file.py")

    assert result == "bp_My__file_20260331_123456"


def test_target_path_helper_converts_to_import_and_test_paths():
    helper = TargetPathHelper()

    assert (
        helper.to_import_path("core/helpers/target_path_helper.py")
        == "core.helpers.target_path_helper"
    )
    assert helper.to_test_path("core/helpers/target_path_helper.py") == (
        "tests/core/helpers/test_target_path_helper.py"
    )
