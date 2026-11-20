
from pydantic import BaseModel, Field
from uuid import UUID


class AdminActivateOrderRequest(BaseModel):
    order_id: UUID = Field(alias="orderId")
    payment_reference: str = Field(
        alias="paymentReference",
        min_length=1,
        max_length=200
    )

    model_config = {
        "populate_by_name": True
    }
