from pathlib import Path

from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType
from core.writers.work_order_writer import WorkOrderWriter


def test_work_order_writer_writes_json_and_yaml(tmp_path):
    work_order = WorkOrder(
        request_id="r",
        blueprint_name="bp",
        profile_name="default",
        order_type=WorkOrderType.CREATE,
        goal="g",
        payload={"k": "v"},
    )
    WorkOrderWriter().write(work_order, Path(tmp_path))

    assert (Path(tmp_path) / "task.json").exists()
    assert (Path(tmp_path) / "task.yaml").exists()
