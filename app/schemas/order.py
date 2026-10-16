from decimal import Decimal
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.enums import OrderStatus, TargetGroup


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

<<<<<<< Updated upstream
class OrderBaseSchema(BaseSchema):
    pass

class OrderSchema(OrderBaseSchema):
=======

tag_string = Annotated[str, StringConstraints(max_length=40)]


class OrderProductSchema(BaseSchema):
    id: int
    name: Annotated[str, Query(max_length=40)]
    description: Annotated[str, Query(max_length=250)] | None = None
    short_description: Annotated[str, Query(max_length=50)] | None = None
    slug: Annotated[str, Query(max_length=255)]
    thumbnail: str
    tags: list[tag_string] | None = None
    is_featured: bool
    created_at: datetime
    gender: TargetGroup
    base_price: Decimal = Field(max_digits=10, decimal_places=2)


class OrderProductVariantSchema(BaseSchema):
    id: int
    variant_price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int
    is_available: bool
    product: OrderProductSchema


class OrderItemSchema(BaseSchema):
    id: int
    variant: OrderProductVariantSchema
    product_name: str
    quantity: int
    price_paid: Decimal


class OrderSchema(BaseSchema):
>>>>>>> Stashed changes
    id: int
    user_id: int
    order_number: str
    subtotal: Decimal
    shipping_total: Decimal
    total: Decimal
    grand_total: Decimal
    status: OrderStatus
<<<<<<< Updated upstream
=======
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemSchema]

>>>>>>> Stashed changes

class OrderListSchema(BaseSchema):
    orders: list[OrderSchema]
