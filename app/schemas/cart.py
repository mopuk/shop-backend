from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class CartItemCreate(BaseSchema):
    variant_id: int
    quantity: int = 1

class CartVariantSnippet(BaseModel):
    id: int
    price: Decimal = Field(alias="variant_price")
    thumbnail: str | None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CartItemResponse(BaseSchema):
    id: int
    quantity: int
    price_at_addition: Decimal
    variant: CartVariantSnippet

class CartResponse(BaseSchema):
    user_id: int
    items: list[CartItemResponse]
    updated_at: datetime
