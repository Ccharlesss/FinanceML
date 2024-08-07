from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Imports from Configuration:
from src.Configuration.database import get_db
from src.Configuration.security import get_current_user

# Imports from Models:
from src.Models.UserModel import User


# Imports from UserController:
from src.Controllers import UserController

# Imports from Schemas:
from src.Schemas.RoleSchemas import UpdateRoleFields



# ================================================================================================================
#Create a new router for roles-related endpoints 
role_router = APIRouter(prefix='/roles', tags=['Roles'])

### Update the role of a user ###
@role_router.put('/update-role', status_code=status.HTTP_200_OK)
async def update_role(data: UpdateRoleFields, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == "Admin":
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized")
    await UserController.update_user_role(data.email, data.new_role, session)
    return {"message": f"User with email {data.email} has been assigned a new role: {data.new_role}"}


### Get the role of the current user ###
@role_router.get('/get-user-role', status_code=status.HTTP_200_OK)
async def retrieve_role(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    return await UserController.get_user_role(current_user)
