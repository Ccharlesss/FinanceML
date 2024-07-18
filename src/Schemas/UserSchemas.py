from pydantic import BaseModel, EmailStr, Field, constr

class UserBase(BaseModel):
# Base class for common user fields.
  username: str
  email: EmailStr

class UserCreate(UserBase):
# Required fields to create a new user account.
  password: str
