# Review Summary

## Request ID
test_002

## Artifact Type
python_registry_class

## Class Name
ArtifactRegistry

## Source Path
tool/core/generated_registry.py

## Test Path
tests/core/test_generated_registry.py

## Responsibility
Register and retrieve artifact definitions for the CLI tool.

## Expected Methods
- register(definition)
- get(name)
- list_names()

## Behavioral Rules
- register(definition): definition must expose a non-empty string attribute 'name'
- get(name): raise KeyError if the requested name does not exist
- list_names(): return all registered names sorted ascending

## Review Checklist
- Does the source file contain exactly one class?
- Are all required methods present?
- Does register validate definition.name correctly?
- Does get raise KeyError for unknown names?
- Does list_names return sorted names?
- Are type hints included?
- Is a class docstring included?
- Is the pytest file at the exact requested path?
- Was unrelated functionality avoided?
