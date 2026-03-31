import pytest

from core.models.blueprint import Blueprint
from core.registry.registry import Registry


def test_registry_register_get_and_duplicate_guard():
    registry = Registry()
    blueprint = Blueprint(name="bp", component_type="x", required_fields=[])

    registry.register(blueprint)

    assert registry.get("bp") is blueprint

    with pytest.raises(ValueError):
        registry.register(blueprint)

    with pytest.raises(ValueError):
        registry.get("missing")
