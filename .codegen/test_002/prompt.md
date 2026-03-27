# Role
You are an experienced Python engineer.

# Task
Generate exactly two files:
1. One Python source file
2. One pytest test file

# Artifact Type
python_registry_class

# Source File Path
tool/core/generated_registry.py

# Test File Path
tests/core/test_generated_registry.py

# Class Name
ArtifactRegistry

# Responsibility
Register and retrieve artifact definitions for the CLI tool.

# Required Methods
- register(definition)
- get(name)
- list_names()

# Behavioral Requirements
- register(definition): definition must expose a non-empty string attribute 'name'
- get(name): raise KeyError if the requested name does not exist
- list_names(): return all registered names sorted ascending

# Constraints
- Generate exactly one Python class in the source file
- Do not create unrelated helper classes
- Use type hints
- Include a class docstring
- Keep the implementation minimal and readable
- Do not add external dependencies
- Use pytest for tests
- The code must fit into a console application codebase

# Output Format
Return only code.
Use this exact structure:

### FILE: tool/core/generated_registry.py
```python
...code...
