from core.models.work_order import WorkOrder
from core.models.work_order_type import WorkOrderType


def test_work_order_to_dict_serializes_enum_value():
    work_order = WorkOrder(
        request_id="r",
        blueprint_name="bp",
        profile_name="default",
        order_type=WorkOrderType.MODIFY,
        goal="g",
        payload={"k": "v"},
    )

    data = work_order.to_dict()

    assert data["order_type"] == "modify"
    assert data["payload"] == {"k": "v"}
