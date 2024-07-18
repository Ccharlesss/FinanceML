from pydantic import BaseModel, EmailStr
# Imports from Schemas:
from src.Schemas.UserSchemas import UserBase

class VerifyUserFields(BaseModel):
# Fields required for verifying user accounts:
  email: EmailStr
  token: str

class LoginFields(BaseModel):
# Fields required for login in
  # username: str
  email: EmailStr
  password: str

class ResetPasswordFields(UserBase):
# Fields required for setting a new password:
  new_password: str

  