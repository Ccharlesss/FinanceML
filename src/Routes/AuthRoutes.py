from email.header import Header
from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# imports from Configurations:
from src.Configuration.database import get_db
from src.Configuration.security import get_current_user

# import from Models:
from src.Models.UserModel import User

# Imports from Controllers:
from src.Controllers import TokenController, UserController

# Imports from Responses:
from src.Responses.LoginResponse import LoginResponse


# Imports from Schemas
from src.Schemas.AuthSchemas import ResetPasswordFields, LoginFields

notyet_login_router = APIRouter(
    prefix='/auth', 
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)

auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)

### Login w/ OAuth2PasswordRequestForm library which uses username and password in form data not JSON ###
# @notyet_login_router.post('/login', status_code=status.HTTP_200_OK, response_model=LoginResponse)
# async def login(data:OAuth2PasswordRequestForm= Depends(), session:Session=Depends(get_db)):
#     return await UserController.get_login_token(data, session)


### Login w/ email and password in the form of JSON data ###
@notyet_login_router.post('/login', status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login(data:LoginFields, session:Session=Depends(get_db)):
    return await UserController.get_login_token(data, session)

### Reset User password ###
@notyet_login_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetPasswordFields, session: Session = Depends(get_db)):
    await UserController.reset_password(data, session)
    return JSONResponse({"message": "Your password has been updated."})

### Logout ###
@auth_router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    await UserController.logout_user(current_user, session)
    return {"message": "Logout successful"}


### Refresh User Token ###
# @auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=LoginResponse)
# async def refresh_token(refresh_token: str = Header(None), session: Session = Depends(get_db)):
#     return await TokenController.get_refresh_token(refresh_token, session)


@auth_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def refresh_token(refresh_token = Header(None), session: Session = Depends(get_db)):
    return await TokenController.get_refresh_token(refresh_token, session)
