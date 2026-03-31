from core.writers.work_order_proposal_writer import WorkOrderProposalWriter


def test_proposal_writer_writes_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = WorkOrderProposalWriter().write(request_id="r", proposal_text="x")

    assert path.exists()
    assert path.read_text(encoding="utf-8") == "x\n"
