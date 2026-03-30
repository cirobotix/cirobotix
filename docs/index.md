# cirobotix

Architecture-driven code generation pipeline.

## Quality Gates

- pytest
- ruff
- bandit
- vulture
- mkdocs

## WorkOrder Workflow

The current generation workflow is split into three explicit steps:

1. **AI Draft**
   - Command: `make ai-draft TASK=tasks/<task>.yaml`
   - Creates an AI-generated `proposal.yaml` from an Atomic Task.

2. **Promote**
   - Command: `make promote REQUEST_ID=<request_id>`
   - Validates and promotes `proposal.yaml` to `task.yaml`.

3. **Generate**
   - Command: `make generate REQUEST_ID=<request_id>`
   - Runs the production line for the promoted WorkOrder.

Example:

```bash
make ai-draft TASK=tasks/test_output_checker.yaml
make promote REQUEST_ID=test_output_checker
make generate REQUEST_ID=test_output_checker
