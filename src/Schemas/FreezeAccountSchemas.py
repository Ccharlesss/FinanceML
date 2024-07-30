from pydantic import BaseModel, EmailStr

class FreezeAccountFields(BaseModel):
# Required fields to freeze an account:
  email: EmailStr
  username: str