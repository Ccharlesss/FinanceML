from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Imports from Configuration:
from src.Configuration.database import get_db

# Imports from UserController:
from src.Controllers import UserController

# Imports from Schemas:
from src.Schemas.RoleSchemas import AssignRoleFields, UpdateRoleFields



# ================================================================================================================
#Create a new router for roles-related endpoints 
role_router = APIRouter(prefix='/roles', tags=['Roles'])


### Update the role of a user ###
@role_router.put('/update-role', status_code=status.HTTP_200_OK)
async def update_role(data: UpdateRoleFields, session: Session = Depends(get_db)):
    await UserController.update_user_role(data.email, data.new_role, session)
    return {"message": f"User with email {data.email} has been assigned a new role: {data.new_role}"}