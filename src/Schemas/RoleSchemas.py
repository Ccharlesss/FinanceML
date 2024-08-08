from pydantic import BaseModel, EmailStr

class AssignRoleFields(BaseModel):
# Required fields to assign a role to a user:
  email: EmailStr
  role_name:str

class UpdateRoleFields(BaseModel):
# Required fields to update the role of a user:
  # email: EmailStr
  user_id: int
  new_role:str