import pytest

from core.blueprints import catalog


class DummyRegistry:
    def __init__(self) -> None:
        self.calls = []

    def register(self, blueprint):
        self.calls.append(blueprint)


def test_register_blueprints_registers_both_blueprints_in_order(monkeypatch):
    registry = DummyRegistry()
    registry_blueprint = object()
    unittest_blueprint = object()

    monkeypatch.setattr(
        catalog,
        "build_python_registry_class_blueprint",
        lambda: registry_blueprint,
    )
    monkeypatch.setattr(
        catalog,
        "build_python_pytest_unit_test_blueprint",
        lambda: unittest_blueprint,
    )

    catalog.register_blueprints(registry)

    assert registry.calls == [registry_blueprint, unittest_blueprint]


def test_register_blueprints_propagates_builder_errors(monkeypatch):
    registry = DummyRegistry()

    def failing_builder():
        raise RuntimeError("builder failed")

    monkeypatch.setattr(catalog, "build_python_registry_class_blueprint", failing_builder)

    with pytest.raises(RuntimeError, match="builder failed"):
        catalog.register_blueprints(registry)

    assert registry.calls == []


def test_register_blueprints_stops_if_first_register_fails(monkeypatch):
    call_counter = {"second_builder_calls": 0}

    class FailingRegistry:
        def register(self, blueprint):
            raise ValueError("register failed")

    monkeypatch.setattr(catalog, "build_python_registry_class_blueprint", lambda: object())

    def second_builder():
        call_counter["second_builder_calls"] += 1
        return object()

    monkeypatch.setattr(catalog, "build_python_pytest_unit_test_blueprint", second_builder)

    with pytest.raises(ValueError, match="register failed"):
        catalog.register_blueprints(FailingRegistry())

    assert call_counter["second_builder_calls"] == 0
