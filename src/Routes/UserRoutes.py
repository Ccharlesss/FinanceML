from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Imports from Configurations:
from src.Configuration.database import get_db

# Imports from Controllers:
from src.Configuration.security import get_current_user
from src.Controllers import UserController

# Imports from Schemas:
from src.Models.UserModel import User
from src.Schemas.UserSchemas import UserCreate
from src.Schemas.UserSchemas import UpdateUserDetailsField
from src.Schemas.AuthSchemas import VerifyUserFields
from src.Schemas.FreezeAccountSchemas import FreezeAccountFields

# Imports from Responses:
from src.Responses.UserResponse import UserResponse, AccountCreatedResponse

user_router = APIRouter(
    prefix='/users',
    tags=['Users'],
    responses={404: {'description': 'Not found'}},
)

# Purpose: Create a new user account:
@user_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=AccountCreatedResponse)
async def create_user_account(data: UserCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    return await UserController.create_user_account(data, session, background_tasks)

# Purpose: Sent verification link when an account is created:
@user_router.post('/verify-account', status_code=status.HTTP_200_OK)
async def verify_user_account(data: VerifyUserFields, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    await UserController.activate_user_account(data, session, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})


# Purpose: List all users:
@user_router.get('/list-users', status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_all_users(session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == 'Admin':
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized.")
    return await UserController.list_all_users(session)


# Purpose: Block a user's account:
@user_router.put('/block-user-account', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def block_user_account(data: FreezeAccountFields, session:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == "Admin":
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized.")
    user = await UserController.freeze_user_account(data.user_id, session)
    return user

# Purpose: Unblock a user's account
@user_router.put('/unblock-user-account', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def unblock_user_account(data: FreezeAccountFields, session:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == "Admin":
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized.")
    user = await UserController.unfreeze_user_account(data.user_id, session)
    return user


# Purpose: Update user's details:
@user_router.put('/update-user-details', status_code=status.HTTP_200_OK)
async def update_user(data: UpdateUserDetailsField, session:Session = Depends(get_db), current_user:User=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == "Admin":
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized.")
    return await UserController.update_user_details(data.user_id, data.new_username, data.new_user_role, session)

