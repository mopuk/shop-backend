from pydantic import BaseModel, ConfigDict, HttpUrl
from decimal import Decimal
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
class CartItemCreate(BaseSchema):
    variant_id: int
    slug: str
    quantity: int = 1
    
class CartProductSnippet(BaseSchema):
    id: int
    slug: str
    price: Decimal
    image_url: HttpUrl
    
class CartItemResponse(BaseSchema):
    id: int
    quantity: int
    price_at_addition: Decimal
    product: CartProductSnippet
    
class CartResponse(BaseSchema):
    user_id: int
    items: list[CartItemResponse]
    updated_at: datetime
