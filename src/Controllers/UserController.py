from datetime import datetime, timezone
import logging
from venv import logger
from fastapi import BackgroundTasks, HTTPException
from requests import Session

# Imports from Configuration:
from src.Configuration.security import hash_password, is_password_strong_enough, load_user, verify_password
from src.Context.EmailContext import USER_VERIFY_ACCOUNT
# Imports from Models:
from src.Models.UserModel import User
# Imports from Controllers:
from src.Controllers.TokenController import _generate_tokens
# Imports from Responses:
from src.Responses.LoginResponse import LoginResponse
# Imports from Services:
from src.Services.EmailServices import send_account_verification_email


### ========================================================================================================
###                                           CREATE USR ACC / ACTIVATE ACC

### Purpose: Create a user account: ###
async def create_user_account(data, session, background_tasks):
    # 1) Verify if a user with the same email already exists:
    user_exist = session.query(User).filter(User.email == data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")
    
    # 2) Verify if the password is strong enough:
    if not is_password_strong_enough(data.password):
        raise HTTPException(status_code=400, detail="Password isn't strong enough.")
        
    # 3) Store all user credentials into the database:
    user = User()
    user.username = data.username
    user.email = data.email
    user.password = hash_password(data.password)
    user.updated_at = datetime.now(timezone.utc)
    user.created_at = datetime.now(timezone.utc)
    user.is_active = False
    user.is_authenticated = False
    session.add(user)
    session.commit()
    session.refresh(user)

    # 4) Assign the role "user" to the newly created user:
    await assign_role_to_user(data.email, "user", session)

    # 5) Send the account verification email to the newly created user:
    await send_account_verification_email(user, background_tasks=background_tasks)
    
    # 6) Return the newly created user:
    return user




# Purpose: Activate the user account:
async def activate_user_account(data, session: Session, background_tasks: BackgroundTasks):
    # 1) Load user using the load_user function:
    user = await load_user(data.email, session)
    if not user:
        raise HTTPException(status_code=400, detail="No user with this email exists in the database.")
    
    # 2) Generate a new unique string for the account verification process:
    user_token = user.get_context_string(context=USER_VERIFY_ACCOUNT)
    
    # 3) Verify the validity of the token
    try:
        # When user clicks on verification link, they arrive at route /users/auth/verify:
        # user_token is generated using get_context_string(context=USER_VERIFY_ACCOUNT) = Expected token
        # data.token is extracted from the URL query parameters = included in the verification link that the user clicked = token of the user
        # If true: Token provided by user matches expected token generated by app during account creation
        token_valid = verify_password(user_token, data.token)
    except Exception as verify_exec:
        logging.exception(verify_exec)
        token_valid = False
    
    if not token_valid:
        raise HTTPException(status_code=400, detail="This link either expired or is not valid.")
    
    # 4) Activate the user account:
    user.is_authenticated = True
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # 5) Send Email to the user that says Account verification was successful:
    await send_account_verification_email(user, background_tasks)
    return user



### ========================================================================================================
###                                           MANAGE USR ROLES
### Assign a role to a user ###
async def assign_role_to_user(email: str, role_name: str, session: Session):
    """Assigns a role to a user."""
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {email} not found")

    user.role = role_name
    session.commit()


### Update the role of a user ###
# async def update_user_role(email: str, new_role: str, session: Session):
#     """Updates the role of a user."""
#     user = session.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail=f"User with email {email} not found")
    
#     current_role = user.role
#     logger.info(f"Updating role for user {user.email} from {current_role} to {new_role}")
#     user.role = new_role

#     try:
#         session.commit()
#         session.refresh(user)  # Refresh the user instance to reflect the latest state from the database
#         logger.info(f"Role updated successfully for user {user.email} to {user.role}")
#     except Exception as e:
#         session.rollback()
#         logger.error(f"Failed to update role for user {user.email}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")
    




### Update the role of a user ###
async def update_user_role(id: int, new_role: str, session: Session):
    """Updates the role of a user."""
    user = session.query(User).filter(User.email == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {id} not found")
    
    current_role = user.role
    logger.info(f"Updating role for user {user.id} from {current_role} to {new_role}")
    user.role = new_role

    try:
        session.commit()
        session.refresh(user)  # Refresh the user instance to reflect the latest state from the database
        logger.info(f"Role updated successfully for user {user.id} to {user.role}")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update role for user {user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")
    
    

### Get the role of the user ###
async def get_user_role(current_user: User) -> str:
    return current_user.role



async def update_user_name(id: int, new_username: str, session: Session):
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User w/ ID ={id} not found.")
    current_username = user.username
    logger.info(f"Successfully changed username from {current_username} to {new_username}")
    user.username = new_username

    try:
        session.commit()
        session.refresh(user)
        logger.info(f"username successfully changed in the database from {current_username} to {new_username}.")
    except Exception as e:
        session.rollback()
        logger.error("failed to update the username from {current_username} to {new_username}.")
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")
    

async def update_role(user: User, old_role: str, new_role: str, session: Session):
    user.role = new_role
    try:
        session.commit()
        session.refresh(user)
        logger.info(f"Successfully updated user's role from {old_role} to {new_role}")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update the user's role from {old_role} to {new_role}")
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")

async def update_username(user: User, old_username: str, new_username: str, session: Session):
    user.username = new_username
    try:
        session.commit()
        session.refresh(user)
        logger.info(f"Successfully updated username from {old_username} to {new_username}.")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update username from {old_username} to {new_username}.")
        raise HTTPException(status_code=500, detail=f"Failed to update username: {str(e)}")

async def update_user_details(id: int, new_username: str, new_role: str, session: Session):
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID={id} not found.")
    
    current_username = user.username
    current_role = user.role

    if current_username == new_username and current_role != new_role:
        await update_role(user, current_role, new_role, session)
    elif current_username != new_username and current_role == new_role:
        await update_username(user, current_username, new_username, session)
    else:
        user.username = new_username
        user.role = new_role
        logger.info(f"Attempting to change both username and user role.")
        try:
            session.commit()
            session.refresh(user)
            logger.info(f"Successfully changed username to {new_username} and user role to {new_role}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to change username to {new_username} and user role to {new_role}")
            raise HTTPException(status_code=500, detail=f"Failed to update username and role: {str(e)}")






### ========================================================================================================
###                                           LOGIN / LOGOUT FUNC
### Purpose: Logout of the account ###
async def logout_user(current_user: User, session: Session):
    # Invalidate the refresh token associated with the current user
    current_user.refresh_token = None  # Assuming UserModel has a refresh_token attribute
    session.add(current_user)
    session.commit()


### Purpose: Get login token from the user to sign in::
async def get_login_token(data, session):
    # 1) Fetch the user based on the given username:
    # user = await load_user(data.username, session)
    user = await load_user(data.email, session)
    if not user:
        raise HTTPException(status_code=400, detail="user doesn't exist.")
    
    # 2) Verify the password:
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password.")
    
    # 3) Verify user account is active and authenticated:
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Your account isn't active.")
    if not user.is_authenticated:
        raise HTTPException(status_code=400, detail="Your account isn't authenticated.")
    
    # 4) Generate JWT token:
    tokens = await _generate_tokens(user, session)
    
    # 5) Return LoginResponse with tokens and other user details
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
        token_type="Bearer",
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_authenticated=user.is_authenticated,
        roles=user.role  # Assuming 'roles' is a field in your User model that contains a list of roles
    )



### ========================================================================================================
###                                            CHANGE PSW FUNC
### Purpose: Reset user's password: ###
async def reset_password(data, session):
   # 1) Fetch the user from the database based on its email address:
   user = await load_user(data.email, session)
   if not user:
      raise HTTPException(status_code=400, detail="No user with the following email {data.email} has been found.")
   # 2) verify if the username matches the data.username entered:
   if user.username != data.username:
      raise HTTPException(status_code=400, detail="No user with the following usernane {data.username} matches the account linked to the email address.")
   # 3) update the password in the Dd:
   user.password = hash_password(data.new_password)
   user.updated_at = datetime.now(timezone.utc)
   session.add(user)
   session.commit()
   session.refresh(user)     


# Purpose: Fetch the user details from the database
async def fetch_user_detail(pk, session):
    user = session.query(User).filter(User.id == pk).first()
    if user:
        return user
    raise HTTPException(status_code=400, detail="User does not exists.")





### ========================================================================================================
###                                            LIST ALL USERS
async def list_all_users(session: Session):
    try:
        # Query the database to retrieve all users
        users = session.query(User).all()
        return users
    except Exception as e:
        logging.error(f"An error occurred while listing users: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while listing users.")




### ========================================================================================================
###                                            Deactivate User Account
# async def freeze_user_account(data, session: Session):
#     # 1) Try to retrieve the user from the database:
#     user = await load_user(data.email, session)
#     if not user:
#         raise HTTPException(status_code=400, detail="No user with the following email {data.email} has been found.")
#     # 2) Verify if the username retrieved matches the one of the user:
#     if user.username != data.username:
#         raise HTTPException(status_code=400, detail="The Username {data.username} doesn't match the one retrieved from the DB.")
#     # 3) Modify the active status of user to False:
#     user.is_active = False
#     # 4) Attempt to commit this change to the DB:
#     try:
#         session.commit()
#         session.refresh(user)
#         logger.info("User Account has been froozen.")
#         return user
#     except Exception as e:
#         session.rollback()
#         logger.error(f"Failed to freeze user's account: {e}")
#         raise HTTPException(status_code=500, detail="Failed to freeze user's account: {e}")
    

async def freeze_user_account(id: int, session: Session):
    # 1) Try to retrive the user from the database:
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID={id} not found.")
    # 2) Attempt to modify the active status of user to False:
    user.is_active = False
    # 3) Attempt to Commit changes to the DB:
    try:
        session.commit()
        session.refresh(user)
        logger.info(f"User account w/ {id} has been froozen.")
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to freeze user's account: {e}")
        raise HTTPException(status_code=500, detail="Failed to freeze user's account: {e}")
    


    

### ========================================================================================================
###                                            Re-activate User Account
# async def unfreeze_user_account(data, session: Session):
#     # 1) Try to retrieve the user from the database:
#     user = await load_user(data.email, session)
#     if not user:
#         raise HTTPException(status_code=400, detail="No user with the following email {data.email} has been found.")
#     # 2( Verify if the username retrieved matches the one of the user:
#     if user.username != data.username:
#         raise HTTPException(status_code=400, detail="The Username {data.username} doesn't match the one retrieved from the DB.")
#     # 3) Modify the active status of the user to True:
#     user.is_active = True
#     # 4) Attempt to commit this change to the DB:
#     try:
#         session.commit()
#         session.refresh(user)
#         logger.info("User's account has been re-activated.")
#         return user
#     except Exception as e:
#         session.rollback()
#         logger.error(f"Failed to re-activate user's account: {e}")
#         raise HTTPException(status_code=500, detail="Failed to re-activate user's account: {e}")
    

async def unfreeze_user_account(id: int, session: Session):
    # 1) Try to retrive the user from the database:
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID={id} not found.")
    # 2) Attempt to modify the active status of user to False:
    user.is_active = True
    # 3) Attempt to Commit changes to the DB:
    try:
        session.commit()
        session.refresh(user)
        logger.info(f"User account w/ {id} has been unfroozen.")
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to unfreeze user's account: {e}")
        raise HTTPException(status_code=500, detail="Failed to unfreeze user's account: {e}")
    

