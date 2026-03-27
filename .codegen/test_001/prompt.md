# Role
You are an experienced Python engineer.

# Task
Generate exactly one bounded Python class for a console application.

# Artifact Type
python_registry_class

# Target File
tool/core/generated_registry.py

# Class Name
ArtifactRegistry

# Responsibility
Register and retrieve artifact definitions for the CLI tool.

# Required Methods
- register(definition)
- get(name)
- list_names()

# Constraints
- Generate exactly one Python class
- Do not create unrelated helper classes
- Use type hints
- Include a class docstring
- Keep the implementation clean and minimal
- Use clear method names and straightforward logic
- Do not add external dependencies
- The result must fit into a console application codebase

# Additional Output Requirement
Also generate a pytest test file for this class.

# Expected Files
1. Source file: tool/core/generated_registry.py
2. Test file: tests/artifactregistry_test.py

# Acceptance Criteria
- One class only
- Required methods are present
- Code is readable and testable
- pytest tests are included
