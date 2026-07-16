from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
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
    
class UserCreate(UserBase):
    password: str
    
class UserResponse(UserBase):
    id: int
    is_active: bool = True
    role: Role
    created_at: datetime
    
class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    role: Role
    created_at: datetime


    
    