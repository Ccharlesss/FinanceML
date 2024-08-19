from datetime import datetime, timezone
import json
from unittest.mock import MagicMock, patch
import pandas as pd
from pydantic import BaseModel
import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from src.Configuration import settings
from src.Configuration.settings import get_settings
from src.Context.EmailContext import USER_VERIFY_ACCOUNT
from src.Controllers.TokenController import _generate_tokens
from src.Models.UserModel import User
from src.Models.TokenModel import Token
from src.Schemas.UserSchemas import UserCreate
from src.Schemas.AuthSchemas import ResetPasswordFields
from src.Schemas.AuthSchemas import LoginFields
from src.Controllers.UserController import create_user_account, activate_user_account, get_user_role, update_role
from src.Controllers.UserController import update_username, update_user_details, list_all_users, get_login_token
from src.Controllers.UserController import freeze_user_account, unfreeze_user_account, reset_password, fetch_user_detail, logout_user
from src.Configuration.security import get_token_payload, str_decode, verify_password, hash_password, get_current_user, load_user
from src.Services.EmailServices import send_account_verification_email
from src.Unit_test.configtest import client, db_session, app_test  # Import app_test explicitly

from sklearn.cluster import KMeans 
from src.Services.KMeanService import retrieve_data_to_df, compute_avg_annual_return_and_volatility, remove_outliers_iqr, perform_kmeans_and_create_dataframe

from src.Services.RandomForesstService import retrieve_data_from_cvs_to_df, compute_rsi, compute_stochastic_oscillators
from src.Services.RandomForesstService import compute_macd, compute_obv, compute_proc, compute_features_and_remove_nan
from src.Services.RandomForesstService import generate_prediction_column, compute_random_forest

from src.Context.StockContext import CSV_FILE_PATH

from src.Configuration.email import send_email

# Mock data for user creation
mock_data = UserCreate(
    username="testuser",
    email="testuser@example.com",
    password="StrongPassword123$"
)

# Mock data for user creation
mock_data2 = UserCreate(
    username="Amazinguser",
    email="testuser@yahooo.com",
    password="StrongPassword123$"
)



# Mock data for user creation
user_with_same_email = UserCreate(
    username="testuser1",
    email="testuser@example.com",
    password="StrongPassword123$"
)

# Mock data for user creation
weak_user_data = UserCreate(
    username="testuser2",
    email="testuser@example2.com",
    password="Strong"
)


class LoginData(BaseModel):
    email: str
    password: str

settings = get_settings()

# ===================================================================================================================
# Test 1: Create user account w/ strong password:
@pytest.mark.asyncio
async def test_create_user_account_success(client, db_session):
    """Test successful user account creation with a strong password."""
    background_tasks = BackgroundTasks()

    # Call the function to test
    user = await create_user_account(mock_data, db_session, background_tasks)

    # Verify the user was created correctly using dot notation
    assert user.username == mock_data.username  # Use dot notation
    assert user.email == mock_data.email  # Use dot notation
    assert user.is_active is False
    assert user.is_authenticated is False
    assert user.role == "user"

    # Check that the user was saved to the database
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()  # Use dot notation
    assert db_user is not None
    assert db_user.username == mock_data.username
    assert db_user.role == "user"


# ===================================================================================================================
# Test 2: Attempt to create user account with a weak password => Ensure the user account isn't created:
@pytest.mark.asyncio
async def test_create_user_account_with_weak_password(client, db_session):
    """Test user account creation fails with a weak password."""
    background_tasks = BackgroundTasks()


    # 1) Call the function to test and expect it to raise an HTTPException due to weak password
    with pytest.raises(HTTPException) as excinfo:
        await create_user_account(weak_user_data, db_session, background_tasks)

    # 2) Verify the correct error message and status code are raised
    assert excinfo.value.status_code == 400
    assert "Password isn't strong enough." in excinfo.value.detail

    # 3) Ensure no user was created in the database
    db_user = db_session.query(User).filter_by(email=weak_user_data.email).first()
    assert db_user is None


# ===================================================================================================================
# Test 3: Attempt to create user account with a already used Email address: => Ensure the user account isn't created:
@pytest.mark.asyncio
async def test_create_user_with_existing_email(client, db_session):
    """Test user account creation fails with a used email address."""
    background_tasks = BackgroundTasks()
    
    # 1) Create a user account
    user = await create_user_account(mock_data, db_session, background_tasks)

    # 1) Try to create a user with same email Call the function to test and expect it to raise a
    with pytest.raises(HTTPException) as excinfo:
        await create_user_account(user_with_same_email, db_session, background_tasks)
    
    # 2) Verify the correct error message and status code are raised:
    assert excinfo.value.status_code == 400
    assert "A user with this email already exists." in excinfo.value.detail

    # 3) Ensures no user was created in the database:
    db_user = db_session.query(User).filter_by(username=user_with_same_email.username).first()
    assert db_user is None




# ===================================================================================================================
# Test 4: Attempt to create a user and to assess if a confirmation email was sent to the user:
@pytest.mark.asyncio
async def test_email_verification_link_sent(client, db_session):
    """Test if an email verification link is sent when a user account is created."""

    background_tasks = BackgroundTasks()

    # 1) Mock the send_email function} display the path to this function:
    with patch('src.Configuration.email.send_email') as mock_send_email:
        try:
            user = await create_user_account(mock_data, db_session, background_tasks)

            # 2) Check if the user was created in the database
            db_user = db_session.query(User).filter_by(email=mock_data.email).first()
            assert db_user is not None

            # Debugging output
            print(f"User created: {user}")
            print(f"DB User: {db_user}")

            # 3) Assert that send_email was called once:
            assert mock_send_email.call_count == 1, "send_email was not called"

            # 4) Verify that send_email was called with the correct arguments
            mock_send_email.assert_called_with(
                recipients=[mock_data.email],
                subject=f"Account Verification - {get_settings().APP_NAME}",
                template_name="email/account-verification.html",
                context={
                    'app_name': get_settings().APP_NAME,
                    'name': mock_data.username,
                    'activate_url': f'{get_settings().FRONTEND_HOST}/account-verify?token={db_user.hashed_password}&email={mock_data.email}'
                },
                background_tasks=background_tasks
            )

        except Exception as e:
            print("Exception during user creation:", e)




# ===================================================================================================================
# Test 5: Test whether when the user clicks on the verification link, his account gets activated:
@pytest.mark.asyncio
async def test_user_activation_flow(client, db_session):
    """Test the user account activation flow after creating an account."""
    background_tasks = BackgroundTasks()

    # 1) Mock the send_email function} display the path to this function:
    with patch('src.Configuration.email.send_email') as mock_send_email:
        try:
            user = await create_user_account(mock_data, db_session, background_tasks)

            # 2) Check if the user was created in the database
            db_user = db_session.query(User).filter_by(email=mock_data.email).first()
            assert db_user is not None

            # Debugging output
            print(f"User created: {user}")
            print(f"DB User: {db_user}")

            # 3) Assert that send_email was called once:
            assert mock_send_email.call_count == 1, "send_email was not called"
            # Extract the token from the email context (assuming it's generated correctly)
            token = db_user.get_context_string(context=USER_VERIFY_ACCOUNT)

            # Step 3: Simulate clicking the verification link
            activation_data = {
            "email": mock_data.email,
            "token": token
            }
            activated_user = await activate_user_account(activation_data, db_session, background_tasks)

            # Step 4: Verify the user is now activated
            assert activated_user.is_active is True, "User should be active"
            assert activated_user.is_authenticated is True, "User should be authenticated"
        
        except Exception as e:
            print("Exception during user creation:", e)


# ===================================================================================================================
# Test 6: Test the Get_user_role function: 
@pytest.mark.asyncio
async def test_get_user_role(client, db_session):
    """Test the get_user_role function after user account was created """
    background_tasks = BackgroundTasks()

    # 1) Create a new user account:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) get the user role:
    user_role = await get_user_role(user)
    # 3) Assess if the user role = 'user' was returned:
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()
    assert user_role == db_user.role


# ===================================================================================================================
# Test 7: Test the update_role function:
@pytest.mark.asyncio
async def test_update_role(client, db_session):
    """Test the update_role function after user account was created """
    background_tasks = BackgroundTasks()
    # 1) Create a new user account:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Assess the user role stored in the database is == 'user':
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()
    assert user.role == db_user.role
    # 3) Attempt to change the role of the user from 'user' to 'Admin':
    await update_role(user, 'user', 'Admin', db_session)
    db_session.refresh(user)
    assert db_user.role == 'Admin'

# ===================================================================================================================
# Test 8: Test the update_role function when there is a database error
@pytest.mark.asyncio
async def test_update_role_failure(client, db_session):
    """Test the update_role function after user account was created when an error in the database occurred."""
    background_tasks = BackgroundTasks()
    
    # 1) Create a new user account
    user = await create_user_account(mock_data, db_session, background_tasks)

    # 2) Mock the session to raise an exception when committing
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("Database error")

    # 3) Attempt to call the update_role function using the mocked session
    with pytest.raises(HTTPException) as excinfo:
        await update_role(user, 'user', 'Admin', mock_session)  # Pass the mock session here

    assert excinfo.value.status_code == 500
    assert "Failed to update user role" in excinfo.value.detail



# ===================================================================================================================
# Test 9: Test update username function:
@pytest.mark.asyncio
async def test_update_username(client, db_session):
    """Test the  update_username function"""
    background_tasks = BackgroundTasks()
    # 1) Create a new user account:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Assess the user is stored in the database:
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()
    initial_username = user.username
    assert db_user.username == initial_username
    # 3) Attempt to modify the username:
    await update_username(user, initial_username, "CoolNewUsername", db_session)
    # 4) Look into the database to ensure the username has been changed:
    db_session.refresh(user)
    assert db_user.username != initial_username
    assert db_user.username == "CoolNewUsername"


# ===================================================================================================================
# Test 10: Test update username function when there is a database error:
@pytest.mark.asyncio
async def test_update_username_failure(client, db_session):
    """Test the  update_username function when there is a database error"""
    background_tasks = BackgroundTasks()
    # 1) Create a new user account:
    user = await create_user_account(mock_data, db_session, background_tasks)
    initial_username = user.username
    # 2) Mock the session to raise an exception when committing:
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("Database error")
    # 3) Attempt to call the update_username funcion:
    with pytest.raises(HTTPException) as excinfo:
        await update_username(user, initial_username, "CoolNewUsername", mock_session)
    assert excinfo.value.status_code == 500
    assert "Failed to update username:" in excinfo.value.detail


# ===================================================================================================================
# Test 11: Test the update_user_detail function:
@pytest.mark.asyncio
async def test_update_user_details(client, db_session):
    """Test the update_user_detail function"""
    background_tasks = BackgroundTasks()
    # 1) Create a new user account: 
    user = await create_user_account(mock_data, db_session, background_tasks)
    initial_username = user.username
    initial_role = user.role
    # 2) Verify if the user Creation was successful:
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()
    assert db_user.username == initial_username
    assert db_user.role == initial_role
    # 3) Attempt to modify the user detail by adding a new username and a new role:
    new_username = "Jake"
    new_role = "Admin"
    await update_user_details(user.id, new_username, new_role, db_session)
    db_session.refresh(user)
    # 4) Test if the username and role has changed:
    assert db_user.username == new_username
    assert db_user.role == new_role

# ===================================================================================================================
# Test 12: Test the update_user_detail function when the username is the only field to change:
@pytest.mark.asyncio
async def test_update_user_details_only_username(client, db_session):
    """Test the update_user_detail function when the username is the only field to change"""
    background_tasks = BackgroundTasks()
    # 1) Create a new user account:
    user = await create_user_account(mock_data, db_session, background_tasks)
    initial_username = user.username
    initial_role = user.role
    # 2) Verify if the user Creation was successful:
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()
    assert db_user.username == initial_username
    assert db_user.role == initial_role
    # 3) Attempt to modify the user detail by just adding a new username:
    new_username = "Jake"
    await update_user_details(user.id, new_username, initial_role, db_session)
    db_session.refresh(user)
    # 4) Assess if username has changed in the database and if role hasn't changed:
    assert db_user.username == new_username
    assert db_user.role == initial_role

# ===================================================================================================================
# Test 13: Test the update_user_detail function when the role is the only field to change:
@pytest.mark.asyncio
async def test_update_user_details_only_role(client, db_session):
    """Test the update_user_detail function when the role is the only field to change"""
    background_tasks = BackgroundTasks()
    # 1) Create a new user account:
    user = await create_user_account(mock_data, db_session, background_tasks)
    initial_username = user.username
    initial_role = user.role
    # 2) Verify if the user Creation was successful:
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()
    assert db_user.username == initial_username
    assert db_user.role == initial_role
    # 3) Attempt to modify the user detail by just adding a new role:
    new_role = "Admin"
    await update_user_details(user.id, initial_username, new_role, db_session)
    db_session.refresh(user)
    # 4) Assess if username has changed in the database and if role hasn't changed:
    assert db_user.username == initial_username
    assert db_user.role == new_role


# ===================================================================================================================
# Test 14: Test the update_user_detail function when when there is a database error:
@pytest.mark.asyncio
async def test_update_user_details_failure(client, db_session):
    """Test the update_user_detail function when there is a database error"""
    background_tasks = BackgroundTasks()
    # 1) Create a new user account 
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Mock the session to raise an exception when committing:
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("Database error")
    # 3) Attempt to call the update_user_detail function:
    with pytest.raises(HTTPException) as excinfo:
        await update_user_details(user.id, "Jake", "Admin", mock_session)
    assert excinfo.value.status_code == 500
    assert "Failed to update username and role:"


# ===================================================================================================================
# Test 15: Test list all users stored in the database:
@pytest.mark.asyncio
async def test_list_all_users(client, db_session):
    """Test list_all_users when users are stored in teh database"""
    background_tasks = BackgroundTasks()
    # 1) Creating 2 users:
    user1 = await create_user_account(mock_data, db_session, background_tasks)
    user_2 = await create_user_account(mock_data2, db_session, background_tasks)
    # 2) Assess both users are stored in the database:
    db_user1 = db_session.query(User).filter_by(email=mock_data.email).first()
    db_user2 = db_session.query(User).filter_by(email=mock_data2.email).first()
    assert db_user1.username == mock_data.username
    assert db_user2.username == mock_data2.username
    # 3) Attempt to list all users in the database:
    users_list = await list_all_users(db_session)
    # 4) Verify that 2 users are stored in the database:
    assert len(users_list) == 2
    # 5) Check that both users are in the returned list:
    user_usernames = [user.username for user in users_list]
    assert db_user1.username in user_usernames
    assert db_user2.username in user_usernames

# ===================================================================================================================
# Test 16: Test list_all_users when no users are currently stored in the database:
@pytest.mark.asyncio
async def test_list_all_users_when_no_users(client, db_session):
    """Test list_all_users when no users are currently stored in the database"""
    # 1) Assess no users are stored in the database:
    users_in_db = db_session.query(User).all()
    assert len(users_in_db) == 0
    # 2) Attempt to list all users in the database:
    user_list = await list_all_users(db_session)
    # 3) Assess that the user list is empty:
    assert user_list == []

# ===================================================================================================================
# Test 17: Test list_all_users when an error occured in the database:
@pytest.mark.asyncio
async def test_list_all_users_failure(client, db_session):
    """Test list_all_users when a database error occurs"""
    
    # 1) Mock the session's query method to raise an exception when called
    mock_session = MagicMock()
    mock_session.query().all.side_effect = Exception("Database error")
    
    # 2) Attempt to call the list_all_users function
    with pytest.raises(HTTPException) as excinfo:
        await list_all_users(mock_session)
    
    # 3) Check that the correct HTTPException is raised
    assert excinfo.value.status_code == 500
    assert "An error occurred while listing users." in excinfo.value.detail


# ===================================================================================================================
# Test 18: Test whether user's password gets encrypted once in the database:
@pytest.mark.asyncio
async def test_is_password_hashed_in_db(client, db_session):
    """Test if the user's password get's hashed in the database"""
    background_tasks = BackgroundTasks()
    # 1) Create a user account:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Retrieve the user from the database:
    db_user = db_session.query(User).filter_by(email=mock_data.email).first()
    # 3) Assess that the user password is not stored as plain text in the database:
    assert db_user.password != mock_data.password
    # 4) Verify that the hashed password matches the original plain password
    is_password_correct = verify_password(mock_data.password, db_user.password)
    assert is_password_correct 



# # ===================================================================================================================
# # Test 19: Test whether the login function works correctly:
@pytest.mark.asyncio
async def test_get_login_token(client, db_session):
    """Test get_login_token that enables user to login"""
    background_tasks = BackgroundTasks()
    # 1) Mock the send_email function} display the path to this function:
    with patch('src.Configuration.email.send_email') as mock_send_email:
        try:
            user = await create_user_account(mock_data, db_session, background_tasks)
            # 2) Check if the user was created in the database
            db_user = db_session.query(User).filter_by(email=mock_data.email).first()
            assert db_user is not None
            # 3) Assert that send_email was called once:
            assert mock_send_email.call_count == 1, "send_email was not called"
            # 4) Extract the token from the email context (assuming it's generated correctly)
            token = db_user.get_context_string(context=USER_VERIFY_ACCOUNT)
            # 5) Simulate clicking the verification link
            activation_data = {
            "email": mock_data.email,
            "token": token
            }
            # 6) Create the field required for login:
            required_login_data = {
            "email": mock_data.email,
            "password": mock_data.password
            }

            # 6) Activate user account
            activated_user = await activate_user_account(activation_data, db_session, background_tasks)
            # 7) Assess if user's account is activated and authenticated
            assert activated_user.is_active is True, "User should be active"
            assert activated_user.is_authenticated is True, "User should be authenticated"
            # 8) Attempt to login the user:
            result = await get_login_token(required_login_data, db_session)
            # 9) Assess whether the token is return to assess successful login:
            assert result.access_token == token["access_token"]
            assert result.refresh_token == token["refresh_token"]
            assert result.expires_in == token["expires_in"]
            assert result.token_type == "Bearer"
            assert result.username == db_user.username
            assert result.email == db_user.email
            assert result.is_active == activated_user.is_active
            assert result.is_authenticated == activated_user.is_authenticated
            assert result.roles == db_user.role
        except Exception as e:
            print("Exception during user creation:", e)
    

# # ===================================================================================================================
# Test 20: Test whether the login function don't allow signin the user if his credentials are wrong:
@pytest.mark.asyncio
async def test_get_login_token_with_wrong_password(client, db_session):
    """Test get_login_token that enables user to login with wrong password"""
    background_tasks = BackgroundTasks()
    # 1) Mock the send_email function} display the path to this function:
    with patch('src.Configuration.email.send_email') as mock_send_email:
        try:
            user = await create_user_account(mock_data, db_session, background_tasks)
            # 2) Check if the user was created in the database
            db_user = db_session.query(User).filter_by(email=mock_data.email).first()
            assert db_user is not None
            # 3) Assert that send_email was called once:
            assert mock_send_email.call_count == 1, "send_email was not called"
            # 4) Extract the token from the email context (assuming it's generated correctly)
            token = db_user.get_context_string(context=USER_VERIFY_ACCOUNT)
            # 5) Simulate clicking the verification link
            activation_data = {
            "email": mock_data.email,
            "token": token
            }
            # 6) Create the field required for login:
            required_login_data_with_incorrect_password = {
            "email": mock_data.email,
            "password": "IncorrectPassword65"
            }

            # 6) Activate user account
            activated_user = await activate_user_account(activation_data, db_session, background_tasks)
            # 7) Assess if user's account is activated and authenticated
            assert activated_user.is_active is True, "User should be active"
            assert activated_user.is_authenticated is True, "User should be authenticated"
            # 8) Attempt to login with an incorrect password:
            with pytest.raises(HTTPException) as excinfo:
                await get_login_token(required_login_data_with_incorrect_password, db_session, background_tasks)
            assert excinfo.value.status_code == 400
            assert "Invalid password."
        except Exception as e:
            print("Exception during user creation:", e)


# ===================================================================================================================
# Test 21: Test whether the login function don't allow signin the user if his email is wrong:
@pytest.mark.asyncio
async def test_get_login_token_with_wrong_email(client, db_session):
    """Test get_login_token that enables user to login with wrong email"""
    background_tasks = BackgroundTasks()
    # 1) Mock the send_email function} display the path to this function:
    with patch('src.Configuration.email.send_email') as mock_send_email:
        try:
            user = await create_user_account(mock_data, db_session, background_tasks)
            # 2) Check if the user was created in the database
            db_user = db_session.query(User).filter_by(email=mock_data.email).first()
            assert db_user is not None
            # 3) Assert that send_email was called once:
            assert mock_send_email.call_count == 1, "send_email was not called"
            # 4) Extract the token from the email context (assuming it's generated correctly)
            token = db_user.get_context_string(context=USER_VERIFY_ACCOUNT)
            # 5) Simulate clicking the verification link
            activation_data = {
            "email": mock_data.email,
            "token": token
            }
            # 6) Create the field required for login:
            required_login_data_with_incorrect_email = {
            "email": "wrongEmail@yahoo.com",
            "password": mock_data.password
            }

            # 6) Activate user account
            activated_user = await activate_user_account(activation_data, db_session, background_tasks)
            # 7) Assess if user's account is activated and authenticated
            assert activated_user.is_active is True, "User should be active"
            assert activated_user.is_authenticated is True, "User should be authenticated"
            # 8) Attempt to login with an incorrect password:
            with pytest.raises(HTTPException) as excinfo:
                await get_login_token(required_login_data_with_incorrect_email, db_session, background_tasks)
            assert excinfo.value.status_code == 400
            assert "user doesn't exist."
        except Exception as e:
            print("Exception during user creation:", e)

# # ===================================================================================================================
# Test 22: Test whether the login function don't allow signin when is_ative status == false:
@pytest.mark.asyncio
async def test_get_login_token_with_non_active_user(client, db_session):
    """Test whether the login function doesn't allow sign-in when is_active status == False."""
    background_tasks = BackgroundTasks()

    # 1) Create a user object with the required attributes directly
    user = User(
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),  # Ensure the password is hashed
        is_active=False,  # Set is_active to False
        is_authenticated=True,
        role="user"  # Assuming `role` is part of your mock_data
    )

    # 2) Add the user to the database
    db_session.add(user)
    db_session.commit()

    # 3) Prepare the login data as a LoginData instance
    required_login_data = LoginData(
        email=user.email,
        password=mock_data.password
    )

    # 4) Attempt to login with the non-active user:
    with pytest.raises(HTTPException) as excinfo:
        await get_login_token(required_login_data, db_session)

    # 5) Check that the HTTPException is raised with the correct status code and detail
    assert excinfo.value.status_code == 400
    assert str(excinfo.value.detail) == "Your account isn't active."



# ===================================================================================================================
# Test 23: Test whether the login function don't allow signin when is_authenticated status == false:
@pytest.mark.asyncio
async def test_get_login_token_with_non_authenticated_user(client, db_session):
    """Test whether the login function doesn't allow sign-in when is_authenticated status == False."""
    background_tasks = BackgroundTasks()

    # 1) Create a user object with the required attributes directly
    user = User(
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),  # Ensure the password is hashed
        is_active=True,  # Set is_active to False
        is_authenticated=False,
        role="user"  # Assuming `role` is part of your mock_data
    )

    # 2) Add the user to the database
    db_session.add(user)
    db_session.commit()

    # 3) Prepare the login data as a LoginData instance
    required_login_data = LoginData(
        email=user.email,
        password=mock_data.password
    )

    # 4) Attempt to login with the non-active user:
    with pytest.raises(HTTPException) as excinfo:
        await get_login_token(required_login_data, db_session)

    # 5) Check that the HTTPException is raised with the correct status code and detail
    assert excinfo.value.status_code == 400
    assert str(excinfo.value.detail) == "Your account isn't authenticated."


# ===================================================================================================================
# Test 24: Test the function that enable to block a user account:
@pytest.mark.asyncio
async def test_freeze_user_account(client, db_session):
    """Test freeze_user_account to set the is_active status from true to false"""
    background_tasks = BackgroundTasks()

    # 1) Create a user object with the required attributes directly
    user = User(
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),  # Ensure the password is hashed
        is_active=True,  # Set is_active to False
        is_authenticated=True,
        role="user"  # Assuming `role` is part of your mock_data
    )
    # 2) Add the user to the database
    db_session.add(user)
    db_session.commit()
    # 3) Get user stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    # 3) Try to block block the user_account
    await freeze_user_account(user_db.id, db_session)
    db_session.refresh(user)
    # 4) Assess if the is_active status in the user is changed to false:
    assert user_db.is_active == False


# ===================================================================================================================
# Test 25: Test the function that enable to unblock a user account:
@pytest.mark.asyncio
async def test_unfreeze_user_account(client, db_session):
    """Test freeze_user_account to set the is_active status from false to true"""
    background_tasks = BackgroundTasks()

    # 1) Create a user object with the required attributes directly
    user = User(
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),  # Ensure the password is hashed
        is_active=False,  # Set is_active to False
        is_authenticated=True,
        role="user"  # Assuming `role` is part of your mock_data
    )
    # 2) Add the user to the database
    db_session.add(user)
    db_session.commit()
    # 3) Get user stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    # 3) Try to block block the user_account
    await unfreeze_user_account(user_db.id, db_session)
    db_session.refresh(user)
    # 4) Assess if the is_active status in the user is changed to false:
    assert user_db.is_active == True



# ===================================================================================================================
# Test 26: Test the function that freeze a user account when the wrong id is provided
@pytest.mark.asyncio
async def test_freeze_user_account_failure(client, db_session):
    """Test freeze_user_account to set the is_active status from false to true"""
    background_tasks = BackgroundTasks()

    # 1) Create a user object with the required attributes directly
    user = User(
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),  # Ensure the password is hashed
        is_active=True,  # Set is_active to False
        is_authenticated=True,
        role="user"  # Assuming `role` is part of your mock_data
    )
    # 2) Add the user to the database
    db_session.add(user)
    db_session.commit()
    # 3) Create a fake user_id:
    fake_user_id = 1919
    # 3) Get user stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    # 4) Try to block block the user_account
    with pytest.raises(HTTPException) as excinfo:
        await freeze_user_account(fake_user_id, db_session)
        db_session.refresh(user)
    # 4) Assess that an issue had occured in the data:
    assert excinfo.value.status_code == 404
    assert f"User with ID={fake_user_id} not found."





# ===================================================================================================================
# Test 27: Test the function that unfreeze a user account when the wrong id is provided
@pytest.mark.asyncio
async def test_unfreeze_user_account_failure(client, db_session):
    """Test freeze_user_account to set the is_active status from false to true"""
    background_tasks = BackgroundTasks()

    # 1) Create a user object with the required attributes directly
    user = User(
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),  # Ensure the password is hashed
        is_active=False,  # Set is_active to False
        is_authenticated=True,
        role="user"  # Assuming `role` is part of your mock_data
    )
    # 2) Add the user to the database
    db_session.add(user)
    db_session.commit()
    # 3) Create a fake user_id:
    fake_user_id = 1919
    # 3) Get user stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    # 4) Try to block block the user_account
    with pytest.raises(HTTPException) as excinfo:
        await unfreeze_user_account(fake_user_id, db_session)
        db_session.refresh(user)
    # 4) Assess that an issue had occured in the data:
    assert excinfo.value.status_code == 404
    assert f"User with ID={fake_user_id} not found."


# ===================================================================================================================
# Test 28: Test the reset_password function with correct strong password:
@pytest.mark.asyncio
async def test_reset_password_with_strong_password(client, db_session):
    """Test reset password function with strong new password"""
    background_tasks = BackgroundTasks()
    # 1) Create a user:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Look at the hash password stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    initial_psw = user_db.password
    # 2) Create required field to change password:
    new_strong_psw = ResetPasswordFields(
        username=mock_data.username,
        email=mock_data.email,
        new_password="ThisIsMyNewStrongPSW64$"
    )
    # 3) Attempt to change password:
    await reset_password(new_strong_psw, db_session)
    # 4) Assert if the hashed password in the database has changed:
    db_session.refresh(user)
    assert user_db.password != initial_psw

# ===================================================================================================================
# Test 29: Test the reset_password function with correct weak password:
@pytest.mark.asyncio
async def test_reset_password_with_weak_password(client, db_session):
    """Test reset password function with strong new password"""
    background_tasks = BackgroundTasks()
    # 1) Create a user:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Look at the hash password stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    initial_psw = user_db.password
    # 3) Create required field to change password:
    new_strong_psw = ResetPasswordFields(
        username=mock_data.username,
        email=mock_data.email,
        new_password="new"
    )
    # 4) Attempt to change password:
    with pytest.raises(HTTPException) as excinfo:
        await reset_password(new_strong_psw, db_session)
    # 4) Assert if the hashed password in the database has changed:
    assert excinfo.value.status_code == 400
    assert "Password isn't strong enough."

# ===================================================================================================================
# Test 30: Test the reset_password function with the incorrect username:
@pytest.mark.asyncio
async def test_reset_password_with_incorrect_username(client, db_session):
    """Test reset password function with strong new password"""
    background_tasks = BackgroundTasks()
    # 1) Create a user:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Look at the hash password stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    initial_psw = user_db.password
    # 3) Create required field to change password:
    new_strong_psw = ResetPasswordFields(
        username="Mark",
        email=mock_data.email,
        new_password="DDDrkjaiewj234"
    )
    # 4) Attempt to change password:
    with pytest.raises(HTTPException) as excinfo:
        await reset_password(new_strong_psw, db_session)
    # 4) Assert if the hashed password in the database has changed:
    assert excinfo.value.status_code == 400
    assert "No user with the following usernane {new_strong_psw.username} matches the account linked to the email address."


# ===================================================================================================================
# Test 31: Test the reset_password function with the incorrect email:
@pytest.mark.asyncio
async def test_reset_password_with_incorrect_email(client, db_session):
    """Test reset password function with strong new password"""
    background_tasks = BackgroundTasks()
    # 1) Create a user:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) Look at the hash password stored in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    initial_psw = user_db.password
    # 3) Create required field to change password:
    new_strong_psw = ResetPasswordFields(
        username=mock_data.username,
        email="ericGorge@yahoo.com",
        new_password="DDDrkjaiewj234"
    )
    # 4) Attempt to change password:
    with pytest.raises(HTTPException) as excinfo:
        await reset_password(new_strong_psw, db_session)
    # 4) Assert if the hashed password in the database has changed:
    assert excinfo.value.status_code == 400
    assert "No user with the following email {new_strong_psw.email} has been found."

# ===================================================================================================================
# Test 32: Test the fetch_user_detail from the database with correct user id:
@pytest.mark.asyncio
async def test_fetch_user_detail(client, db_session):
    """Test fetch_user_detail from db with correct user id""" 
    background_tasks = BackgroundTasks()
    # 1) Create a user:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) get the user from the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    # 3) Attempt to fetch user details from the database
    user_details = await fetch_user_detail(user_db.id, db_session)
    # 4) Assess whether user's detail were returned
    assert user_details.username == mock_data.username
    assert user_details.email == mock_data.email
    assert user_details.id == user_db.id
    assert user_details.password == user_db.password
    assert user_details.is_active == user_db.is_active
    assert user_details.is_authenticated == user_db.is_authenticated
    assert user_details.role == user_db.role

# ===================================================================================================================
# Test 33: Test the fetch_user_detail from the database with incorrect id:
@pytest.mark.asyncio
async def test_fetch_user_detail_with_wrongID(client, db_session):
    """Test fetch_user_detail from db with incorrect user id"""
    background_tasks = BackgroundTasks()
    # 1) Create a user:
    user = await create_user_account(mock_data, db_session, background_tasks)
    # 2) create an incorrect id:
    incorrect_id = 2934
    # 3) Attempt to fetch user details from the database
    with pytest.raises(HTTPException) as excinfo:
        await fetch_user_detail(incorrect_id, db_session)
    assert excinfo.value.status_code == 400
    assert "User does not exists."



# ===================================================================================================================
# Test 34: Test the logout function:
@pytest.mark.asyncio
async def test_logout_user(client, db_session):
    """Test logout_user function"""
    background_tasks = BackgroundTasks()
    # 1) Create a user object with the required attributes directly:
    user = User(
        id = 5,
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),
        is_active=True,  
        is_authenticated=True,
        role="user"  
    )
    # 2) Add the user to the database:
    db_session.add(user)
    db_session.commit()
    # 3) create required field for the user to login:
    login_fields = LoginFields(
        email = mock_data.email,
        password = mock_data.password
    )
    # 4) Login the user:
    await get_login_token(login_fields, db_session)
    # 5) Attempt to logout:
    await logout_user(user, db_session)
    # 6) Assess whether it correctly removed the user's token:
    token_db = db_session.query(Token).filter_by(user_id = 5).all()
    assert token_db == []
    

# ===================================================================================================================
# Test 35: Test _generate_token function:
@pytest.mark.asyncio
async def test_generate_tokens_success(client, db_session):
    """Test _generate_token function"""
    user_data = mock_data  # Ensure mock_data has the necessary attributes

    user = User(
        id=5,
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        is_active=True,
        is_authenticated=True,
        role="user"
    )

    db_session.add(user)
    db_session.commit()

    # Act
    result = await _generate_tokens(user, db_session)

    # Assert
    assert "access_token" in result
    assert "refresh_token" in result
    assert "expires_in" in result

    # Verify tokens in the database
    token_in_db = db_session.query(Token).filter(Token.user_id == user.id).first()
    assert token_in_db is not None
    assert token_in_db.refresh_key is not None
    assert token_in_db.access_key is not None

    # Ensure both datetimes are timezone-aware
    current_time = datetime.now(timezone.utc)
    token_expires_at = token_in_db.expires_at

    # Ensure token_expires_at is timezone-aware
    if token_expires_at.tzinfo is None:
        token_expires_at = token_expires_at.replace(tzinfo=timezone.utc)

    # Debugging the types of datetime objects
    print(f"Current time: {current_time}")
    print(f"Token expires_at: {token_expires_at}")
    print(f"Type of current_time: {type(current_time)}")
    print(f"Type of token_expires_at: {type(token_expires_at)}")

    # Comparison
    assert token_expires_at > current_time

    # Decode and check token payloads
    access_payload = get_token_payload(result["access_token"], settings.JWT_SECRET, settings.JWT_ALGORITHM)
    refresh_payload = get_token_payload(result["refresh_token"], settings.SECRET_KEY, settings.JWT_ALGORITHM)

    assert str_decode(access_payload["sub"]) == str(user.id)
    assert str_decode(refresh_payload["sub"]) == str(user.id)
    assert access_payload["a"] == token_in_db.access_key

    # Additional assertions for refresh token payload
    assert refresh_payload["t"] == token_in_db.refresh_key

# ===================================================================================================================
# Test 36: Test get_current_user function:
@pytest.mark.asyncio
async def test_get_current_user(client, db_session):
    """Test get_current_user function"""
    background_tasks = BackgroundTasks()
    # 1) Add an active user in the database:
    user = User(
        id=5,
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),
        is_active=True,
        is_authenticated=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    # 2) Login the user and store the token in a variable:
    login_field = LoginFields(
        email = mock_data.email,
        password = mock_data.password
    )
    response = await get_login_token(login_field, db_session)
    # 3) Assess if we can get the user from the token:
    retrieved_user = await get_current_user(response.access_token, db_session)
    assert retrieved_user.email == user.email
    assert retrieved_user.username == user.username
    assert retrieved_user.id == user.id
    assert retrieved_user.is_active == user.is_active
    assert retrieved_user.is_authenticated == user.is_authenticated
    assert retrieved_user.role == user.role


# ===================================================================================================================
# Test 37: Test the load_user function_
@pytest.mark.asyncio
async def test_load_user(client, db_session):
    """Test load_user with correct email"""
    # 1) Create a user and store it in the database:
    user = User(
        id=5,
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),
        is_active=True,
        is_authenticated=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    # 2) Load the user using his email:
    fetched_user = await load_user(mock_data.email, db_session)
    # 3) Assess if his credentials are correct:
    assert fetched_user.username == mock_data.username
    assert fetched_user.email == mock_data.email
    assert fetched_user.id == user.id
    assert fetched_user.is_active == user.is_active
    assert fetched_user.is_authenticated == user.is_authenticated
    assert fetched_user.role == user.role

# ===================================================================================================================
#                                               Testing the KmeanService.py

# Test 38: Test retrieve_data_to_df function:
@pytest.mark.asyncio
async def test_retrieve_data_to_df(client, db_session):
    """Test the retrieve_data_to_df function"""
    # 1) call the function that retrieves the training dataset from the CSV file to a panda df:
    result = await retrieve_data_to_df()
    # 2) Assess if the returned object is a panda dataframe
    assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"

    # Check if the DataFrame is not empty
    assert not result.empty, "DataFrame should not be empty"

    # Check if the DataFrame has the expected columns
    expected_columns = ['Ticker', 'Close']
    assert all(col in result.columns for col in expected_columns), f"DataFrame should contain columns {expected_columns}"

    # Check if the DataFrame has 'Date' as the index
    assert result.index.name == 'Date', "DataFrame index should be 'Date'"



# ===================================================================================================================
# Test 39: Test compute_annual_return_and_volatility:
@pytest.mark.asyncio
async def test_compute_annual_return_and_volatility(client, db_session):
    """Test the compute_avg_annual_return_and_volatility function."""
    
    # 1) Retrieve data to a DataFrame
    initial_data = await retrieve_data_to_df()
    
    # 2) Compute the average annual return and volatility of all stocks
    result = await compute_avg_annual_return_and_volatility(initial_data)
    
    # 3) Assert the result is a DataFrame
    assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
    
    # 4) Check if the DataFrame has the expected columns
    expected_columns = ['Avr Annual Return', 'Avr Annual Volatility']
    assert all(col in result.columns for col in expected_columns), f"DataFrame should contain columns {expected_columns}"
    
    # 5) Check if the result is not empty
    assert not result.empty, "Result DataFrame should not be empty"
    
    # 6) Check for NaN values
    assert not result.isnull().values.any(), "Result DataFrame should not contain NaN values"


# ===================================================================================================================
# Test 40: Test remove_outliers_iqr function:
@pytest.mark.asyncio
async def test_remove_outliers_iqr():
    """Test the remove_outliers_iqr function."""
    
    # 1) Create test data with known outliers and non-outliers
    data = {
        'Avr Annual Return': [0.1, 0.2, 0.3, 0.4, 0.5, 5.0],  # 5.0 is an outlier
        'Avr Annual Volatility': [0.1, 0.2, 0.3, 0.4, 0.5, 5.0]  # 5.0 is an outlier
    }
    df = pd.DataFrame(data)
    
    # 2) Apply the function to remove outliers
    df_no_outliers = await remove_outliers_iqr(df)
    
    # 3) Define the expected DataFrame after outliers are removed
    expected_data = {
        'Avr Annual Return': [0.1, 0.2, 0.3, 0.4, 0.5],
        'Avr Annual Volatility': [0.1, 0.2, 0.3, 0.4, 0.5]
    }
    expected_df = pd.DataFrame(expected_data)
    
    # 4) Check if the result matches the expected DataFrame
    pd.testing.assert_frame_equal(df_no_outliers, expected_df, check_like=True)

# ===================================================================================================================
# Test 41: Test perform_kmeans_and_create_dataframe function
@pytest.mark.asyncio
async def test_perform_kmeans_and_create_dataframe(client, db_session):
    """Test the perform_kmeans_and_create_dataframe function"""
    # 1) Retrieve data to a DataFrame:
    initial_data = await retrieve_data_to_df()
    # 2) Compute the average annual return and volatility of all stocks:
    df_with_features = await compute_avg_annual_return_and_volatility(initial_data)
    # 3) Remove outliers:
    df_with_no_outliers = await remove_outliers_iqr(df_with_features)
    # 4) compute the kmean algorithm:
    result = await perform_kmeans_and_create_dataframe(df_with_no_outliers)
    # 5) Parse the JSON back into a Python dictionary
    result_dict = json.loads(result)
    # 6) Define the expected keys
    expected_keys = ['Ticker', 'Avr Annual Return', 'Avr Annual Volatility', 'Cluster']
    # 7) Check if each item in the JSON contains the required keys
    for item_key, item_value in result_dict.items():
        assert all(key in item_value for key in expected_keys), f"Missing expected keys in item {item_key}"


# ===================================================================================================================
# Test 42: Test retrieve_data_from_csv_to_df function:
@pytest.mark.asyncio
async def test_retrieve_data_from_cvs_to_df(client, db_session):
    """Test the function that retrieves data from csv and converts it to panda DF"""
    # 1) Retrieve the data related to a particular ticker from the CSV:
    result = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) Assess the the returned obj is a pd DataFrame:
    assert isinstance(result, pd.DataFrame)
    # 3) Assess the returned dataframe is not empty or none:
    assert result is not None and not result.empty
    # 4) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['High', 'Low', 'Close', 'Volume']
    assert all(col in result.columns for col in expected_columns)
    # 5) Ensure the 'Date' column is set as the index:
    assert result.index.name == 'Date'

# ===================================================================================================================
# Test 43: Test compute_rsi function:
@pytest.mark.asyncio
async def test_compute_rsi(client, db_session):
    """Test the function that computes the relative strength index (RSI)"""
    # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) Compute the RSI:
    result = await compute_rsi(raw_data)
    # 3) Assess the the returned obj is a pd DataFrame:
    assert isinstance(result, pd.DataFrame)
    # 4) Assess the returned dataframe is not empty or none:
    assert result is not None and not result.empty
    # 5) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['High', 'Low', 'Close', 'Volume', 'RSI']
    assert all(col in result.columns for col in expected_columns)
    # 6) Ensure the 'Date' column is set as the index:
    assert result.index.name == 'Date'
    # 7) Ensure the RSI column is not empty:
    assert not result["RSI"].isnull().all()

# ===================================================================================================================
# Test 44: Test compute_stochastic_oscillator function:
@pytest.mark.asyncio
async def test_compute_stochastic_oscillators(client, db_session):
    """Test the function that computes the stochastic oscillator = {K%, D%, R%}"""
    # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) Compute the RSI:
    df_with_rsi = await compute_rsi(raw_data)
    # 3) Compute the stochastic oscillator:
    result = await compute_stochastic_oscillators(df_with_rsi)
    # 4) Assess the returned object is of type pd.DataFrame:
    assert isinstance(result, pd.DataFrame)
    # 5) Assess if the returned DataFrame is not empty or None:
    assert result is not None and not result.empty
    # 6) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['High', 'Low', 'Close', 'Volume', 'RSI', 'K%', 'D%', 'R%']
    assert all(col in result.columns for col in expected_columns)
    # 7) Ensure the 'Date' column is set as the index:
    assert result.index.name == 'Date'
    # 8) Ensures K%, D% and R% aren't empty:
    assert not result[["K%", "D%", "R%"]].isnull().all().any()

# ===================================================================================================================
# Test 45: Test compute_macd function:
@pytest.mark.asyncio
async def test_compute_macd(client, db_session):
    """Test the function that computes macd"""
     # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) Compute the RSI:
    df_with_rsi = await compute_rsi(raw_data)
    # 3) Compute the stochastic oscillator:
    df_with_so = await compute_stochastic_oscillators(df_with_rsi)
    # 4) Compute the MACD indicators:
    result = await compute_macd(df_with_so)
    # 5) Assess that the returned object is of nature a pd.DataFrame
    assert isinstance(result, pd.DataFrame)
    # 6) Assess that the returned DF isn't empty or None:
    assert result is not None and not result.empty
    # 7) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['High', 'Low', 'Close', 'Volume', 'RSI', 'K%', 'D%', 'R%', 'MACD', 'MACD_Signal', 'MACD_Diff']
    assert all(col in result.columns for col in expected_columns)
    # 8) Assess the date is set as index:
    assert result.index.name == "Date"
    # 9) Assess the computed columns = ['MACD', 'MACD_Signal', 'MACD_Diff'] arent empty:
    assert not result[['MACD', 'MACD_Signal', 'MACD_Diff']].isnull().all().any()

# ===================================================================================================================
# Test 46: Test compute_obv function:
@pytest.mark.asyncio
async def test_compute_obv(client, db_session):
    """Test the function that computes OBV """
    # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) Compute the RSI:
    df_with_rsi = await compute_rsi(raw_data)
    # 3) Compute the stochastic oscillator:
    df_with_so = await compute_stochastic_oscillators(df_with_rsi)
    # 4) Compute the MACD indicators:
    df_with_macd = await compute_macd(df_with_so)
    # 5) Compute the OBV:
    result = await compute_obv(df_with_macd)
    # 6) Assess that the returned object is by nature a pd.DataFrame:
    assert isinstance(result, pd.DataFrame)
    # 7) Assess that the returned DF isn't empty or None:
    assert result is not None and not result.empty
    # 8) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['High', 'Low', 'Close', 'Volume', 'RSI', 'K%', 'D%', 'R%', 'MACD', 'MACD_Signal', 'MACD_Diff',"OBV"]
    assert all(col in result.columns for col in expected_columns)
    # 9) Assess the date is set as index:
    assert result.index.name == "Date"
    # 10) Assess the computed column = ["OBV"] is not empty:
    assert not result[["OBV"]].isnull().all().any()

# ===================================================================================================================
# Test 47: Test compute_proc function:
@pytest.mark.asyncio
async def test_compute_proc(client, db_session):
    """Test the function that computes OBV """
    # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) Compute the RSI:
    df_with_rsi = await compute_rsi(raw_data)
    # 3) Compute the stochastic oscillator:
    df_with_so = await compute_stochastic_oscillators(df_with_rsi)
    # 4) Compute the MACD indicators:
    df_with_macd = await compute_macd(df_with_so)
    # 5) Compute the OBV:
    df_with_obv = await compute_obv(df_with_macd)
    # 6) Compute PROC
    result = await compute_proc(df_with_obv)
    # 8) Assess that the returned object is by nature a pd.DataFrame:
    assert isinstance(result, pd.DataFrame)
    # 9) Assess that the returned DF isn't empty or None:
    assert result is not None and not result.empty
    # 10) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['High', 'Low', 'Close', 'Volume', 'RSI', 'K%', 'D%', 'R%', 'MACD', 'MACD_Signal', 'MACD_Diff',"OBV", "PROC"]
    assert all(col in result.columns for col in expected_columns)
    # 11) Assess the date is set as index:
    assert result.index.name == "Date"
    # 12) Assess the computed column = ["OBV"] is not empty:
    assert not result[["PROC"]].isnull().all().any()

# ===================================================================================================================
# Test 48: Test compute_features_and_remove_nan function:
@pytest.mark.asyncio
async def test_compute_features_and_remove_nan(client, db_session):
    """Test the function that computes the entire feature set = {'RSI', 'K%', 'D%', 'R%', 'MACD', 'MACD_Signal', 'MACD_Diff',"OBV", "PROC"}"""
    # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) plot the raw data in the function to compute all its features:
    result = await compute_features_and_remove_nan(raw_data)
    # 3) Asses that the returned object is a pd.DataFrame:
    assert isinstance(result, pd.DataFrame)
    # 4) Assess that the returned DF isn't empty or None:
    assert result is not None and not result.empty
    # 5) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['High', 'Low', 'Close', 'Volume', 'RSI', 'K%', 'D%', 'R%', 'MACD', 'MACD_Signal', 'MACD_Diff',"OBV", "PROC"]
    assert all(col in result.columns for col in expected_columns)
    # 6) Assess the date is set as index:
    assert result.index.name == "Date"
    # 7) Ensure the DataFrame does not contain any NaN values:
    assert not result.isnull().values.any()

# ===================================================================================================================
# Test 49: Test generate_prediction_column function:
@pytest.mark.asyncio
async def test_generate_prediction_column(client, db_session):
    """Test the generate_prediction_column function """
    # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) plot the raw data in the function to compute all its features:
    df_with_features = await compute_features_and_remove_nan(raw_data)
    # 3) Generate the prediction column:
    result = await generate_prediction_column(df_with_features)
    # 4) Asses that the returned object is a pd.DataFrame:
    assert isinstance(result, pd.DataFrame)
    # 5) Assess that the returned DF isn't empty or None:
    assert result is not None and not result.empty
    # 6) Assess if the returned dataframe contains the expected columns: (excluding 'Date' since it's now the index):
    expected_columns = ['RSI', 'K%', 'D%', 'R%', 'MACD', 'MACD_Signal', 'MACD_Diff',"OBV", "PROC", "Prediction"]
    assert all(col in result.columns for col in expected_columns)
    # 7) Assess the date is set as index:
    assert result.index.name == "Date"
    # 8) Assess the prediction column contains only binary values btw 0 / 1
    assert result["Prediction"].isin([0,1]).all()


# ===================================================================================================================
# Test 50: Test compute_random_forest function:
@pytest.mark.asyncio
async def test_compute_random_forest(client, db_session):
    """Test the compute_random_forest function"""
    # 1) Retrieve the data related to a particular ticker from the CSV:
    raw_data = await retrieve_data_from_cvs_to_df('AAPL')
    # 2) plot the raw data in the function to compute all its features:
    df_with_features = await compute_features_and_remove_nan(raw_data)
    # 3) Generate the prediction column:
    df_with_prediction = await generate_prediction_column(df_with_features)
    # 4) Fit the dataframe to the RF model:
    result = await compute_random_forest(df_with_prediction)
    # 5) Assess if the returned result is in binary format = {0/1}
    assert result in {0, 1}


