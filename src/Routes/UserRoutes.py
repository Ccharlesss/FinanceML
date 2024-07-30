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
from src.Schemas.AuthSchemas import VerifyUserFields
from src.Schemas.FreezeAccountSchemas import FreezeAccountFields

# Imports from Responses:
from src.Responses.UserResponse import UserResponse, AccountCreatedResponse

user_router = APIRouter(
    prefix='/users',
    tags=['Users'],
    responses={404: {'description': 'Not found'}},
)


@user_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=AccountCreatedResponse)
async def create_user_account(data: UserCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    return await UserController.create_user_account(data, session, background_tasks)

@user_router.post('/verify-account', status_code=status.HTTP_200_OK)
async def verify_user_account(data: VerifyUserFields, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    await UserController.activate_user_account(data, session, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})


@user_router.get('/list-users', status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_all_users(session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == 'Admin':
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized.")
    return await UserController.list_all_users(session)



@user_router.put('/deactivate-user-account', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def deactivate_user_account(data: FreezeAccountFields, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == "Admin":
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized")
    # await UserController.freeze_user_account(data, session)
    # return {"message": f"User with email {data.email} and username {data.username} has been deactivated"}
    user = await UserController.freeze_user_account(data, session)
    return user


@user_router.put('/reactivate-user-account', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def reactiveate_user_account(data: FreezeAccountFields, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")
    if not current_user.role == "Admin":
        raise HTTPException(status_code=401, detail="Not an Admin thus not authorized")
    # return await UserController.unfreeze_user_account(data, session)
    # return {"message": f"User with email {data.email} and username {data.username} has been reactivated"}
    user = await UserController.unfreeze_user_account(data, session)
    return user 