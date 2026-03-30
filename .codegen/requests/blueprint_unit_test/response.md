### FILE: tests/core/test_blueprint.py
```python
import pytest
from core.blueprint import Blueprint

def test_blueprint_creation_happy_path():
    bp = Blueprint(
        name="TestBlueprint",
        component_type="TypeA",
        required_fields=["field1", "field2"]
    )
    assert bp.name == "TestBlueprint"
    assert bp.component_type == "TypeA"
    assert bp.required_fields == ["field1", "field2"]
    assert bp.description == ""
    assert bp.output_files == []
    assert bp.constraints == []
    assert bp.quality_requirements == []
    assert bp.default_invariants == []

def test_blueprint_required_fields_missing():
    with pytest.raises(TypeError):
        Blueprint(name="TestBlueprint", component_type="TypeA")

def test_blueprint_immutability():
    bp = Blueprint(
        name="TestBlueprint",
        component_type="TypeA",
        required_fields=["field1", "field2"]
    )
    with pytest.raises(AttributeError):
        bp.name = "NewName"

def test_blueprint_list_default_independence():
    bp1 = Blueprint(
        name="TestBlueprint1",
        component_type="TypeA",
        required_fields=["field1", "field2"]
    )
    bp2 = Blueprint(
        name="TestBlueprint2",
        component_type="TypeB",
        required_fields=["field3", "field4"]
    )
    bp1.output_files.append("file1.txt")
    assert bp2.output_files == []
```