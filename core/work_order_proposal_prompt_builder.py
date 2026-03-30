from .atomic_task import AtomicTask
from .blueprint import Blueprint


class WorkOrderProposalPromptBuilder:
    def build(
        self,
        *,
        blueprint: Blueprint,
        task: AtomicTask,
        assembled_context: str,
        suggested_read_files: list[str],
        suggested_writable_files: list[str],
    ) -> str:
        required_fields = (
            "\n".join(f"- {field_name}" for field_name
                      in blueprint.required_fields) or "- none"
        )

        constraints = "\n".join(f"- {item}" for item
                                in blueprint.constraints) or "- none"

        quality_requirements = (
            "\n".join(f"- {item}" for item
                      in blueprint.quality_requirements) or "- none"
        )

        default_invariants = (
            "\n".join(f"- {item}" for item
                      in blueprint.default_invariants) or "- none"
        )

        task_inputs = (
            "\n".join(f"- {key}: {self._format_value(value)}"
                      for key, value in task.inputs.items())
            or "- none"
        )

        task_acceptance = "\n".join(f"- {item}" for item
                                    in task.acceptance_criteria) or "- none"

        suggested_read_files_text = (
            "\n".join(f"- {path}" for path
                      in suggested_read_files) or "- none"
        )

        suggested_writable_files_text = (
            "\n".join(f"- {path}" for path
                      in suggested_writable_files) or "- none"
        )

        return f"""# Role
You are a senior software architecture assistant.

# Task
Create a WorkOrder proposal in YAML format.

You must use:
- the Blueprint as the execution standard
- the Atomic Task as the concrete assignment
- the Existing Code Context as the primary source for realistic payload 
content, read_files, and behavioral expectations

# Blueprint
- Name: {blueprint.name}
- Component Type: {blueprint.component_type}
- Description: {blueprint.description}

## Blueprint Required Fields
{required_fields}

## Blueprint Constraints
{constraints}

## Blueprint Quality Requirements
{quality_requirements}

## Blueprint Default Invariants
{default_invariants}

# Atomic Task
- Task ID: {task.task_id}
- Blueprint Name: {task.blueprint_name}
- Title: {task.title}

## Description
{task.description}

## Inputs
{task_inputs}

## Atomic Task Acceptance Criteria
{task_acceptance}

# Existing Code Context
{assembled_context or "No code context provided."}

# Suggested Files
These file suggestions were derived from project analysis and should be used 
unless the code context clearly proves they are unnecessary.

## Suggested Read Files
{suggested_read_files_text}

## Suggested Writable Files
{suggested_writable_files_text}

# Output Goal
Return exactly one valid YAML WorkOrder proposal.

# WorkOrder YAML Schema
request_id: <string>
blueprint_name: <string>
profile_name: <string>
order_type: <create|modify>
goal: <string>

payload:
  <key>: <value>

read_files:
  - <path>

writable_files:
  - <path>

invariants:
  - <string>

acceptance_criteria:
  - <string>

# Rules
- Use the blueprint name from the atomic task.
- Use request_id equal to the atomic task id unless there is a strong reason to
 derive a more specific id.
- Use profile_name: default unless the atomic task explicitly requires another 
profile.
- Use order_type: create unless the task clearly describes a modification of an 
existing writable target.
- The proposal must be fully consistent with the blueprint constraints and 
quality requirements.
- The invariants must include the blueprint default invariants.
- The acceptance_criteria must include:
  - the blueprint quality requirements
  - the atomic task acceptance criteria
- Prefer the suggested read_files and writable_files when they match the code 
context.
- Do not invent unrelated files.
- Use the code context to infer realistic responsibility, definition_contract, 
happy_path_behavior, and error_behavior.
- Do not use generic placeholder values such as 'Developer', 'Tests the class 
functionalities', or similarly vague text.
- If this is a unit test blueprint, do not propose production source files as 
writable output unless the atomic task explicitly requests it.
- Keep the proposal focused and minimal.
- Return YAML only.
- Do not include markdown fences.
- Do not include explanations.
- The acceptance_criteria section must explicitly include every atomic task 
acceptance criterion, preserving their meaning.
- Every field listed under Blueprint Required Fields must appear in the payload 
section.
- Do not omit any required payload field, even if the value is already implied 
elsewhere.
- If the generated test code needs to simulate FILE block response content, 
build that content from string fragments or line joins inside Python code.
- Do not embed nested raw FILE block fixtures in a way that could be 
interpreted as additional outer output blocks.

# Final Check
Before returning the YAML, verify:
- The YAML is syntactically valid.
- All required fields are present.
- The payload contains the fields required by the blueprint.
- The payload descriptions are specific to the actual target code.
- The read_files are realistic for the target and its direct dependencies.
- The writable_files are precise and minimal.
- The proposal is specific to the atomic task and code context.
- Every atomic task acceptance criterion is present in acceptance_criteria.
- Every blueprint required field is present in payload exactly once when 
applicable.
"""

    def _format_value(self, value):
        if isinstance(value, list):
            if not value:
                return "[]"
            return "[" + ", ".join(str(item) for item in value) + "]"
        return str(value)
