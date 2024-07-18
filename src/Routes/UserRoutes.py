from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Imports from Configurations:
from src.Configuration.database import get_db

# Imports from Controllers:
from src.Controllers import UserController

# Imports from Schemas:
from src.Schemas.UserSchemas import UserCreate
from src.Schemas.AuthSchemas import VerifyUserFields

# Imports from Responses:
from src.Responses.UserResponse import UserResponse, AccountCreatedResponse

user_router = APIRouter(
    prefix='/users',
    tags=['Users'],
    responses={404: {'description': 'Not found'}},
)


#### Create a new User account: ###
@user_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=AccountCreatedResponse)
async def create_user_account(data: UserCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    return await UserController.create_user_account(data, session, background_tasks)


### Verify new User account: ###
@user_router.post('/verify-account', status_code=status.HTTP_200_OK)
async def verify_user_account(data: VerifyUserFields, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    await UserController.activate_user_account(data, session, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})


### List all users: ###
@user_router.get('/list-users', status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_all_users(session: Session = Depends(get_db)):
    return await UserController.list_all_users(session)

