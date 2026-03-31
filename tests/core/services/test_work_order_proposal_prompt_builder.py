from core.models.atomic_task import AtomicTask
from core.models.blueprint import Blueprint
from core.services.work_order_proposal_prompt_builder import WorkOrderProposalPromptBuilder


def test_build_prompt_contains_expected_sections_and_formats():
    builder = WorkOrderProposalPromptBuilder()
    blueprint = Blueprint(
        name="bp",
        component_type="x",
        required_fields=["f1"],
        constraints=["c1"],
        quality_requirements=["q1"],
        default_invariants=["i1"],
    )
    task = AtomicTask(
        task_id="t1",
        blueprint_name="bp",
        title="title",
        description="desc",
        inputs={"k": [1, 2]},
        acceptance_criteria=["a1"],
    )

    prompt = builder.build(
        blueprint=blueprint,
        task=task,
        assembled_context="ctx",
        suggested_read_files=["a.py"],
        suggested_writable_files=["b.py"],
    )

    assert "# Blueprint" in prompt
    assert "- f1" in prompt
    assert "[1, 2]" in prompt
    assert "- a.py" in prompt
    assert "- b.py" in prompt


def test_format_value_handles_empty_list():
    assert WorkOrderProposalPromptBuilder()._format_value([]) == "[]"
    assert WorkOrderProposalPromptBuilder()._format_value(7) == "7"
