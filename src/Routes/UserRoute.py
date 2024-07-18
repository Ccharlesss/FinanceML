from email.header import Header
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.Configuration.database import get_db
from src.Configuration.security import get_current_user
# from src.Controllers.RoleController import assign_role, create_role, update_role
from src.Schemas.UserSchema import AssignRoleRequest, EmailRequest, ResetNewPasswordRequest, UpdateRoleRequest, User, VerifyUserRequest

from src.Responses.UserResponse import UserResponse
from src.Responses.LoginResponse import LoginResponse

from src.Controllers import TokenController, UserController
from src.Configuration.security import oauth2_scheme




user_router = APIRouter(
  prefix='/users', 
  tags=['Users'],
  responses={404: {'description': 'Not found'}},
)

notyet_login_router = APIRouter(
  prefix='/auth', 
  tags=['Auth'],
  responses={404: {'description': 'Not found'}},
)

auth_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme), Depends(get_current_user)]
)


role_router = APIRouter(
    prefix='/roles',
    tags=['Roles'],
    responses={404: {'description': 'Not found'}}
)






# When User creates an account: 
# 1) send_account_verification_email() is called which generates a temporary JWT token. (This token is sent to the user via email for account verification)
# 2) send a send verification link. When user clicks on verification link.
# 3) user is redirected to route /users/auth/verify:
@user_router.post('', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(data:User, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
  return await UserController.create_user_account(data, session, background_tasks)

# When User is in the rout /users/auth/verify:
# 1) Verify_user_account() is called. activate_user_account(): is called
# 2) Extract the token from URL = data.token this is the token the user receives in the email and clicked on
# 3) Generate the expeced token = user_token
# 4) Compares the received token = data.token w/ expected token = user_token
@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user_account(data: VerifyUserRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    await UserController.activate_user_account(data, session, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})


# When user logs into his account: 
# 1) User is expected to type his credentials: username and passowrd and calls user_login().
# 2) data: OAuth2PasswordRequestForm = Depends(): => extract the username and password from the request body.
# 3) calls get_login_token(data=username & password, session=instance of db).
# 4) Returns a JWT token if login successful.
@notyet_login_router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def user_login(data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    return await UserController.get_login_token(data, session)

# When user needs to obtain a new access and refresh token afteir their current access token has expired:
# Header() in the FastAPI route definition is used to extract the refresh_token from the HTTP request headers
# refresh_token = Header() is used, FastAPI looks for a header named refresh_token in the incoming HTTP request.
# If the header is found, its value is passed to the refresh_token
# 1) Refresh token is extracted from the request header
# 2) get_refresh_token() is called to generate and return new access and refresh tokens.
@notyet_login_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def refresh_token(refresh_token = Header(), session: Session = Depends(get_db)):
    return await TokenController.get_refresh_token(refresh_token, session)


# When the user clicks on forgot-password:
@notyet_login_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: EmailRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    await UserController.email_forgot_password_link(data, background_tasks, session)
    return JSONResponse({"message": "A email with password reset link has been sent to you."})

@notyet_login_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetNewPasswordRequest, session: Session = Depends(get_db)):
    await UserController.reset_password(data, session)
    return JSONResponse({"message": "Your password has been updated."})

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def fetch_user(UserServices = Depends(get_current_user)):
    return UserServices

@auth_router.get("/{pk}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_info(pk, session: Session = Depends(get_db)):
    return await UserController.fetch_user_detail(pk, session)

































# @notyet_login_router.put("/reset-password", status_code=status.HTTP_200_OK)
# async def reset_password(data: ResetPasswordRequest, session: Session = Depends(get_db)):
#     await UserController.reset_user_password(data, session)
#     return JSONResponse({"message": "Your password has been updated."})


# @role_router.delete('/remove/{role_id}', status_code=status.HTTP_200_OK)
# async def remove_existing_role(role_id: int, session: Session = Depends(get_db)):
#     return await remove_role(role_id, session)