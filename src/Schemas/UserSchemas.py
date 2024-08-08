from pydantic import BaseModel, EmailStr, Field, constr

class UserBase(BaseModel):
# Base class for common user fields.
  username: str
  email: EmailStr

class UserCreate(UserBase):
# Required fields to create a new user account.
  password: str

class UpdateUsernameField(BaseModel):
  # Required fields to update user's username:
  user_id: int
  new_username: str


class UpdateUserDetailsField(BaseModel):
  # Required fields to update user:
  user_id: int
  new_username: str
  new_user_role: str
