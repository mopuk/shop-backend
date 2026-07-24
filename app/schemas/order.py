from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from app.enums import OrderStatus

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
class OrderBaseSchema(BaseSchema):
    pass
   
class OrderSchema(OrderBaseSchema):
    id: int
    user_id: int
    order_number: str
    subtotal: Decimal
    shipping_total: Decimal
    total: Decimal
    grand_total: Decimal
    status: OrderStatus
    
class OrderListSchema(OrderBaseSchema):
    orders: list[OrderSchema]