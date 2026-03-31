from pathlib import Path


class WorkOrderProposalWriter:
    def write(self, *, request_id: str, proposal_text: str) -> Path:
        base_dir = Path(".codegen") / "requests" / request_id
        base_dir.mkdir(parents=True, exist_ok=True)

        proposal_path = base_dir / "proposal.yaml"
        proposal_path.write_text(proposal_text.rstrip() + "\n", encoding="utf-8")

        return proposal_path
