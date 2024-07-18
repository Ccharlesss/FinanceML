from pydantic import BaseModel, EmailStr

class FieldsForEmail(BaseModel):
# required field to send emails:
  email: EmailStr


