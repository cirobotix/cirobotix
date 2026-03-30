from pathlib import Path
from core.cli_args import CliArgsParser
from core.work_order_cli_service import WorkOrderCliService
from core.work_order_proposal_service import WorkOrderProposalService


DEFAULT_PROJECT_CONFIG = "config/projects/local_project.yaml"
DEFAULT_PROFILE = "default"


def print_step_results(step_results) -> None:
    print("\n📊 STEP RESULTS:")
    for step in step_results:
        status = "✅" if step.success else "❌"
        print(f"{status} {step.machine_name}: {step.message}")


def run_draft(args: dict) -> None:
    blueprint_name = args["blueprint"]
    target_path = args["file"]
    project_config = args.get("project", DEFAULT_PROJECT_CONFIG)
    profile_name = args.get("profile", DEFAULT_PROFILE)

    service = WorkOrderCliService()
    task_path = service.create_draft(
        blueprint_name=blueprint_name,
        target_path=target_path,
        project_config_path=project_config,
        profile_name=profile_name,
    )

    print("✅ WORK ORDER DRAFT CREATED")
    print(f"- Task YAML: {task_path}")
    print(f"- Review: {task_path.parent / 'review.md'}")


def run_ai_draft_workorder(args: dict) -> None:
    task_path = args["task"]
    profile_name = args.get("profile", DEFAULT_PROFILE)
    project_config = args.get("project", DEFAULT_PROJECT_CONFIG)

    service = WorkOrderProposalService()
    proposal_path = service.create_ai_proposal(
        task_path=task_path,
        profile_name=profile_name,
        project_config_path=project_config,
    )

    print("✅ AI WORK ORDER PROPOSAL CREATED")
    print(f"- Proposal YAML: {proposal_path}")


def run_promote_workorder(args: dict) -> None:
    proposal_path = args["proposal"]
    project_config = args.get("project", DEFAULT_PROJECT_CONFIG)

    service = WorkOrderProposalService()
    task_path = service.promote_proposal(
        proposal_path=proposal_path,
        project_config_path=project_config,
    )

    print("✅ WORK ORDER PROPOSAL PROMOTED")
    print(f"- Task YAML: {task_path}")
    print(f"- Review: {Path(task_path).parent / 'review.md'}")


def run_generate(args: dict) -> None:
    work_order_path = args["work_order"]
    project_config = args.get("project", DEFAULT_PROJECT_CONFIG)

    service = WorkOrderCliService()
    context = service.generate(
        work_order_path=work_order_path,
        project_config_path=project_config,
    )

    print(f"LLM output written to: {context.response_path}")

    print("\n✅ APPLIED FILES:")
    for file_path in context.written_files:
        print(f"- {file_path}")

    print("✅ PRODUCTION LINE COMPLETED")
    print_step_results(context.step_results)


def main() -> None:
    args = CliArgsParser().parse()
    command = args.get("command")

    if not command:
        raise ValueError("Missing required argument: command")

    if command == "draft":
        run_draft(args)
        return

    if command == "ai-draft-workorder":
        run_ai_draft_workorder(args)
        return

    if command == "promote-workorder":
        run_promote_workorder(args)
        return

    if command == "generate":
        run_generate(args)
        return

    raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
