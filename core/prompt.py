class PromptBuilder:
    def build(self, request) -> str:
        payload = request.payload
        methods = "\n".join(f"- {method}" for method in payload["methods"])

        return f"""# Role
You are an experienced Python engineer.

# Task
Generate exactly two files:
1. One Python source file
2. One pytest test file

# Artifact Type
{request.artifact_type}

# Source File Path
{payload['target_path']}

# Test File Path
{payload['test_path']}

# Class Name
{payload['class_name']}

# Responsibility
{payload['responsibility']}

# Required Methods
{methods}

# Behavioral Requirements
- register(definition): {payload['definition_contract']}
- get(name): {payload['get_behavior']}
- list_names(): {payload['list_behavior']}

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

### FILE: {payload['target_path']}
```python
...code...
"""