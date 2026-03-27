### FILE: tool/core/generated_registry.py
```python
class ArtifactRegistry:
    """Register and retrieve artifact definitions for the CLI tool."""

    def __init__(self):
        self._registry = {}

    def register(self, definition: object) -> None:
        """Register an artifact definition."""
        if not hasattr(definition, 'name') or not isinstance(definition.name, str) or not definition.name:
            raise ValueError("Definition must have a non-empty string attribute 'name'")
        
        self._registry[definition.name] = definition

    def get(self, name: str) -> object:
        """Retrieve an artifact definition by name."""
        if name not in self._registry:
            raise KeyError(f"Artifact '{name}' not found")
        
        return self._registry[name]

    def list_names(self) -> list[str]:
        """List all registered artifact names sorted ascending."""
        return sorted(self._registry.keys())
```

### FILE: tests/core/test_generated_registry.py
```python
import pytest
from tool.core.generated_registry import ArtifactRegistry

class MockDefinition:
    def __init__(self, name: str):
        self.name = name


def test_register_valid_definition():
    registry = ArtifactRegistry()
    definition = MockDefinition("artifact1")
    registry.register(definition)

    assert registry.get("artifact1") == definition
    assert registry.list_names() == ["artifact1"]


def test_register_invalid_definition():
    registry = ArtifactRegistry()
    
    with pytest.raises(ValueError, match="must have a non-empty string attribute 'name'"):
        registry.register(MockDefinition(""))  # Empty name
    
    with pytest.raises(ValueError, match="must have a non-empty string attribute 'name'"):
        registry.register(object())  # No name attribute


def test_get_nonexistent_definition():
    registry = ArtifactRegistry()

    with pytest.raises(KeyError, match="Artifact 'nonexistent' not found"):
        registry.get("nonexistent")


def test_list_names_empty():
    registry = ArtifactRegistry()
    assert registry.list_names() == []
```