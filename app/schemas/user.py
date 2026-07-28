from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.enums import Role


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class Token(BaseSchema):
    access_token: str
    token_type: str

class TokenData(BaseSchema):
    user_id: int

class UserBase(BaseSchema):
    email: EmailStr
    username: str

class UserCreateSchema(UserBase):
    password: str

class UserResponseSchema(UserBase):
    id: int
    is_active: bool = True
    role: Role
    created_at: datetime
