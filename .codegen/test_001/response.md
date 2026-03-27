Here are the requested files.

### `tool/core/generated_registry.py`
```python
class ArtifactRegistry:
    """Register and retrieve artifact definitions for the CLI tool."""

    def __init__(self) -> None:
        self._definitions: dict[str, object] = {}

    def register(self, definition: object) -> None:
        name = getattr(definition, "name", None)
        if not isinstance(name, str) or not name:
            raise ValueError("definition must have a non-empty string 'name' attribute")
        self._definitions[name] = definition

    def get(self, name: str) -> object:
        return self._definitions[name]

    def list_names(self) -> list[str]:
        return sorted(self._definitions.keys())
```

### `tests/artifactregistry_test.py`
```python
import pytest

from tool.core.generated_registry import ArtifactRegistry


def test_register_and_get_definition() -> None:
    registry = ArtifactRegistry()
    definition = type("Definition", (), {"name": "build"})()

    registry.register(definition)

    assert registry.get("build") is definition


def test_list_names_returns_sorted_names() -> None:
    registry = ArtifactRegistry()
    first = type("Definition", (), {"name": "deploy"})()
    second = type("Definition", (), {"name": "build"})()

    registry.register(first)
    registry.register(second)

    assert registry.list_names() == ["build", "deploy"]


def test_register_requires_non_empty_string_name() -> None:
    registry = ArtifactRegistry()
    invalid_definition = object()

    with pytest.raises(ValueError):
        registry.register(invalid_definition)


def test_get_raises_key_error_for_unknown_name() -> None:
    registry = ArtifactRegistry()

    with pytest.raises(KeyError):
        registry.get("missing")
```