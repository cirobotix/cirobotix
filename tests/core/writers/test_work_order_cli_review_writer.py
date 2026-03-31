from pathlib import Path

from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.writers.work_order_cli_review_writer import WorkOrderCliReviewWriter


def test_write_generates_review_file(tmp_path):
    work_order = WorkOrder(
        request_id="r",
        blueprint_name="bp",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        goal="g",
        payload={},
    )

    WorkOrderCliReviewWriter().write(work_order, Path(tmp_path))

    assert (Path(tmp_path) / "review.md").exists()
