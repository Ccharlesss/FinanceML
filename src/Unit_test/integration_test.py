# ============================================================================================================
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from src.Context.EmailContext import USER_VERIFY_ACCOUNT
from src.Models.TokenModel import Token
from src.Schemas.AuthSchemas import VerifyUserFields
from src.main import app  # Adjust this import to your actual FastAPI app path
from src.Configuration.database import get_db, Base  # Adjust this import to your actual SQLAlchemy config
from src.Configuration.security import hash_password, verify_password
from src.Models.UserModel import User  # Adjust this import to your actual User model path
from src.Schemas.UserSchemas import UserCreate  # Adjust this import to your actual UserCreate schema path
from src.Schemas.AuthSchemas import LoginFields
from src.Schemas.AuthSchemas import ResetPasswordFields
from src.Schemas.UserSchemas import UpdateUserDetailsField
from src.Schemas.FreezeAccountSchemas import FreezeAccountFields

# PostgreSQL container configuration
POSTGRES_IMAGE = "postgres:14"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "test_password"
POSTGRES_DATABASE = "test_database"
POSTGRES_CONTAINER_PORT = 5432

@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer: # type: ignore
    """
    Set up PostgreSQL container.
    """
    postgres = PostgresContainer(
        image=POSTGRES_IMAGE,
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DATABASE,
        port=POSTGRES_CONTAINER_PORT,
    )
    with postgres:
        postgres.start()
        yield postgres

@pytest.fixture(scope="session")
def engine(postgres_container: PostgresContainer):
    """
    Set up SQLAlchemy engine.
    """
    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False, future=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="session")
def db_session(engine):
    """
    Set up SQLAlchemy session.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        yield session

@pytest.fixture(scope="session")
def test_client(db_session):
    """
    Create a TestClient with FastAPI app, overriding the database session.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


mock_data = UserCreate(
    username="adminuser",
    email="admin@example.com",
    password="StrongPassword123$"
)

user_mock_data = UserCreate(
    username="Jake",
    email="jake@example.com",
    password="StrongPassword123$"
)

# ============================================================================================================
# Test 1: Create a user account w/ strong password
@pytest.mark.asyncio
async def test_create_account_route_with_strong_password(test_client, db_session):
    """Test creating a new account with a strong password."""
    # 1) Define mock data:
    mock_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        password="StrongPassword123$"
    )

    # 2)Perform the request:
    response = test_client.post("/users/signup", json={
        'username': mock_data.username,
        'email': mock_data.email,
        'password': mock_data.password
    })

    # 3) Get the JSON response:
    response_data = response.json()
    print(response_data)  # This will help you see the actual structure

    # 4) Assess if the user account was created w/ status_code:
    assert response.status_code == 201
    # 5) Assess the username and email matches and are returned:
    assert 'username' in response_data
    assert response_data['username'] == mock_data.username
    assert response_data['email'] == mock_data.email
    # 6) Verify the user was created in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    assert user_db is not None
    assert user_db.username == mock_data.username
    assert user_db.email == mock_data.email
    assert user_db.role == 'user'
    assert user_db.is_active == False
    assert user_db.is_authenticated == False
    # 7) Verify the password hash:
    assert verify_password(mock_data.password, user_db.password) 


# ============================================================================================================
# Test 2: Create a user account w/ weak password:
@pytest.mark.asyncio
async def test_create_account_route_with_weak_password(test_client, db_session):
    """Test creating a new account with a weak password."""
    # 1) Define the mock data:
    mock_data = UserCreate(
        username="testuser",
        email="testuser1@example.com",
        password="weakpassword"
    )

    # 2) Perform the request:
    response = test_client.post("/users/signup", json={
        'username': mock_data.username,
        'email': mock_data.email,
        'password': mock_data.password
    })

    # 3) Get the JSON response:
    response_data = response.json()
    # 4) Assess if the user account creation failed:
    assert response.status_code == 400
    # 5) Assess the correct error message is returned:
    assert 'detail' in response_data
    assert response_data['detail'] == "Password isn't strong enough."
    # 6) Ensure user was not created in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    assert user_db is None

# ============================================================================================================
# Test 3: Create a user account w/ email already taken:
@pytest.mark.asyncio
async def test_create_account_route_with_existing_email(test_client, db_session):
    """Test creating a new account with an email already used by another account."""
    # 3) Attempt to create a secondary user with the same email:
    mock_data = UserCreate(
        username="NewUser",
        email="testuser@example.com",
        password="StrongPassword123$"
    )

    # 4) Post the request to the appropriate endpoint:
    response = test_client.post("/users/signup", json={
        'username': mock_data.username,
        'email': mock_data.email,
        'password': mock_data.password
    })
    # 5) Get the JSON response:
    response_data = response.json()
    # 6) Assess the user account creation process failed:
    assert response.status_code == 400
    # 7) Assess the appropriate error message is returned:
    assert 'detail' in response_data
    assert response_data['detail'] == "A user with this email already exists."
    # 8) Assess that the user wasnt created and stored in the database:
    user_db = db_session.query(User).filter_by(username=mock_data.username).first()
    assert user_db is None


# ============================================================================================================
# Test 4: Test account activation after a user has been created:
@pytest.mark.asyncio
async def test_verify_account_route(test_client, db_session):
    """Test verifying a user account after creation."""
    # 1) Define mock data for account creation:
    mock_data = UserCreate(
        username="testuser3",
        email="testuse3@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the request to create a new account:
    response = test_client.post("/users/signup", json={
        'username': mock_data.username,
        'email': mock_data.email,
        'password': mock_data.password
    })

    # 3) Assert the user account was created successfully:
    assert response.status_code == 201

    # 4) Retrieve the created user from the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    assert user_db is not None

    # 5) Check that the account is not active and not authenticated before verification:
    assert user_db.is_active is False  # User should not be active before verification
    assert user_db.is_authenticated is False  # User should not be authenticated before verification

    # 6) Simulate the generation of a verification token:
    # Generate a context string for account verification similar to what is done in the email function.
    user_token_context_string = user_db.get_context_string(context=USER_VERIFY_ACCOUNT)
    # Hash the context string to create the token (this is what the email link would contain):
    verification_token = hash_password(user_token_context_string)

    # 7) Simulate clicking on the verification link by calling the verification route:
    verification_data = VerifyUserFields(token=verification_token, email=user_db.email)
    response = test_client.post("/users/verify-account", json={
        'token': verification_data.token,
        'email': verification_data.email
    })

    # 8) Assert the account verification response is successful:
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['message'] == "Account is activated successfully."

    # 9) Re-fetch the user to verify the account status in the database:
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    assert user_db.is_active is True  # Ensure the account is now active after verification
    assert user_db.is_authenticated is True  # Ensure the account is now authenticated after verification


# ============================================================================================================
# Test 5: Test login route with correct credentials:
@pytest.mark.asyncio
async def test_login_route_with_correct_credentials(test_client, db_session):
    """Test login route with correct credentials:"""
    # 1) Utilise login credentials of the first user acount created and activated successfully:
    login_credentials = LoginFields(
        email="testuse3@example.com",
        password="StrongPassword123$"
    )
    
    # 2) Request POST Login endpoint with the login_credentials as payload:
    response = test_client.post("/auth/login", json={
        'email': login_credentials.email,
        'password': login_credentials.password
    })
    # 3) Get the JSON response:
    response_data = response.json()
    # 4) Assess the status code equal to 200:
    assert response.status_code == 200
    # 5) Assert the login response is successful:
    login_response_data = response.json()
    assert 'access_token' in login_response_data
    assert 'refresh_token' in login_response_data
    assert 'expires_in' in login_response_data
    assert login_response_data['token_type'] == 'Bearer'
    # 6) Verify the token is not empty:
    assert login_response_data['access_token'] != ""
    assert login_response_data['refresh_token'] != ""


# ============================================================================================================
# Test 6: Test login route with incorrect password:
@pytest.mark.asyncio
async def test_login_route_with_incorrect_password(test_client, db_session):
    """Test login route with correct credentials:"""
    # 1) Utilise login credentials of a valid account but with a wrong password
    login_credentials = LoginFields(
        email="testuse3@example.com",
        password="wrongPassword123$"
    )
    
    # 2) Request POST Login endpoint with the login_credentials as payload:
    response = test_client.post("/auth/login", json={
        'email': login_credentials.email,
        'password': login_credentials.password
    })
    # 3) Get the JSON response:
    response_data = response.json()
    # 4) Assess that the login was unsuccessful:
    assert response.status_code == 400
    assert response_data['detail'] == "Invalid password."




# ============================================================================================================
# Test 7: Test login route with incorrect email:
@pytest.mark.asyncio
async def test_login_route_with_incorrect_email(test_client, db_session):
    """Test login route with correct email:"""
    # 1) Utilise login credentials of a valid account but with a wrong password
    login_credentials = LoginFields(
        email="false@example.com",
        password="StrongPassword123$"
    )
    
    # 2) Request POST Login endpoint with the login_credentials as payload:
    response = test_client.post("/auth/login", json={
        'email': login_credentials.email,
        'password': login_credentials.password
    })
    # 3) Get the JSON response:
    response_data = response.json()
    # 4) Assess that the login was unsuccessful:
    assert response.status_code == 400
    assert response_data['detail'] == "user doesn't exist."



# ============================================================================================================
# Test 8: Test login route with an inactivate account:
@pytest.mark.asyncio
async def test_login_route_with_inactivated_account(test_client, db_session):
    """Test login route with innactivated_account:"""
    # 1) Utilise login credentials of a valid account but with a wrong password
    login_credentials = LoginFields(
        email="testuser@example.com",
        password="StrongPassword123$"
    )
    
    # 2) Request POST Login endpoint with the login_credentials as payload:
    response = test_client.post("/auth/login", json={
        'email': login_credentials.email,
        'password': login_credentials.password
    })
    # 3) Get the JSON response:
    response_data = response.json()
    # 4) Assess that the login was unsuccessful:
    assert response.status_code == 400
    assert response_data['detail'] == "Your account isn't active."




# ============================================================================================================
# Test 9: Test logout route:
@pytest.mark.asyncio
async def test_logout_route(test_client, db_session):
    """Test logout route"""
    # 1) Create a valid user and login to get access token
    login_credentials = LoginFields(
        email="testuse3@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token
    response = test_client.post("/auth/login", json={
        'email': login_credentials.email,
        'password': login_credentials.password
    })

    # 3) Assert the login response is successful
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 4) Set up the Authorization header with the access token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 5) Perform the logout request using the Authorization header
    response = test_client.post("/auth/logout", headers=headers)

    # 6) Assert the logout response is successful
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['message'] == "Logout successful"

    # 7) Re-fetch the tokens from the database for the logged-out user
    current_user = db_session.query(User).filter_by(email=login_credentials.email).first()
    user_tokens = db_session.query(Token).filter_by(user_id=current_user.id).all()

    # 8) Verify that all tokens associated with the user have been deleted
    assert len(user_tokens) == 0  # No tokens should exist after logout


# ============================================================================================================
# Test 10: Test Reset password route with correct email and strong password:
@pytest.mark.asyncio
async def test_reset_password_route_with_correct_email_and_strong_password(test_client, db_session):
    """Test Reset password route with correct email and strong password"""
    # 1) Define the required fields to change password:
    new_password_field = ResetPasswordFields(
        username="testuser3",
        email="testuse3@example.com",
        new_password="NewStrongPassword123$"
    )
    # 2) Sent the request to the appropriate route:
    response = test_client.put("/auth/reset-password", json={
        'username':new_password_field.username,
        'email':new_password_field.email,
        'new_password':new_password_field.new_password
    })
    # 3) Assert the account reset password was successfully achieved
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['message'] == "Your password has been updated."
    # 4) compares the hashed password stored in the database with the raw new password:
    user_db = db_session.query(User).filter_by(email=new_password_field.email).first()
    is_password_correct = verify_password(new_password_field.new_password, user_db.password)
    assert is_password_correct 


# ============================================================================================================
# Test 11: Test Reset password route with correct email and weak password:
@pytest.mark.asyncio
async def test_reset_password_route_with_correct_email_and_weak_password(test_client, db_session):
    """Test Reset password route with correct email and weak password"""
    # 1) Define the required fields to change password:
    new_password_field = ResetPasswordFields(
        username="testuser3",
        email="testuse3@example.com",
        new_password="weak"
    )
    # 2) Sent the request to the appropriate route:
    response = test_client.put("/auth/reset-password", json={
        'username':new_password_field.username,
        'email':new_password_field.email,
        'new_password':new_password_field.new_password
    })
    # 3) Assert the account reset password was successfully achieved
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['detail'] == "Password isn't strong enough."

# ============================================================================================================
# Test 12: Test Reset password route with incorrect email and strong password:
@pytest.mark.asyncio
async def test_reset_password_route_with_incorrect_email_and_strong_password(test_client, db_session):
    """Test Reset password route with incorrect email and strong password"""
    # 1) Define the required fields to change password:
    new_password_field = ResetPasswordFields(
        username="testuser3",
        email="wrongemail@example.com",
        new_password="NewStrongPassword123$"
    )
    # 2) Sent the request to the appropriate route:
    response = test_client.put("/auth/reset-password", json={
        'username':new_password_field.username,
        'email':new_password_field.email,
        'new_password':new_password_field.new_password
    })
    # 3) Assert the account reset password was successfully achieved
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['detail'] == "No user with the following email {data.email} has been found."



# ============================================================================================================
# Test 13: Test Reset password route with incorrect username and strong password:
@pytest.mark.asyncio
async def test_reset_password_route_with_incorrect_username_and_strong_password(test_client, db_session):
    """Test Reset password route with incorrect username and strong password"""
    # 1) Define the required fields to change password:
    new_password_field = ResetPasswordFields(
        username="wrongusername",
        email="testuse3@example.com",
        new_password="NewStrongPassword123$"
    )
    # 2) Sent the request to the appropriate route:
    response = test_client.put("/auth/reset-password", json={
        'username':new_password_field.username,
        'email':new_password_field.email,
        'new_password':new_password_field.new_password
    })
    # 3) Assert the account reset password was successfully achieved
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['detail'] == "No user with the following usernane {data.username} matches the account linked to the email address."




# ============================================================================================================
# Test 14: Test list-users route with an admin account:
@pytest.mark.asyncio
async def test_list_users_route_with_admin_account(test_client, db_session):
    """Test list-users route with an admin account"""
    # 1) Create an admin and active user:
    user = User(
        id=5,
        username=mock_data.username,
        email=mock_data.email,
        password=hash_password(mock_data.password),
        is_active=True,
        is_authenticated=True,
        role="Admin"
    )
    # 2) Add the newly created admin user in the DB:
    db_session.add(user)
    db_session.commit()

    # 3) Construct the login fields to login the admin:
    login_field = LoginFields(
        email = mock_data.email,
        password = mock_data.password
    )

    # 4) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })
    # 5) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']
    # 6) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 7) Send the list-users request to the appropriate endpoint with Authorization headers:
    response = test_client.get("/users/list-users", headers=headers)    
    # 8) Assert the list-users response is successful:
    assert response.status_code == 200
    # 9) Verify the response data is a list and contains user data:
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0  # Ensure at least one user (admin) is returned
    # 10) Check that each user in the response has the required fields:
    required_fields = {'email', 'username', 'role', 'is_active', 'is_authenticated'}
    for user_data in response_data:
    # Ensure all required fields are in the user data dictionary
        assert required_fields.issubset(user_data.keys())


# ============================================================================================================
# Test 15: Test list-users route with a user account:
@pytest.mark.asyncio
async def test_list_users_route_with_user_account(test_client, db_session):
    """Test list-users route with a user account"""
    # 1) Utilize login credentials of the first user account created and activated successfully:
    login_credentials = LoginFields(
        email="testuse3@example.com",
        password="NewStrongPassword123$"
    )
    
    # 2) Request POST Login endpoint with the login_credentials as payload:
    response = test_client.post("/auth/login", json={
        'email': login_credentials.email,
        'password': login_credentials.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 4) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 5) Send the list-users request to the appropriate endpoint with Authorization headers:
    response = test_client.get("/users/list-users", headers=headers)    
    
    # 6) Assert the response status code is 401 since the user is not an Admin:
    assert response.status_code == 401

    # 7) Assert that the response detail matches the unauthorized message:
    response_data = response.json()
    assert response_data['detail'] == "Not an Admin thus not authorized."


# ============================================================================================================
# Test 16: Test update user's detail route with an admin account (only username is modified)
@pytest.mark.asyncio
async def test_update_users_detail_route_admin_new_username(test_client, db_session):
    """ Test update user's detail route with an admin account (only username is modified) """
    
    # 1) Create an admin user account and activate it:
    admin_user = User(
        id=15,
        username=user_mock_data.username,
        email=user_mock_data.email,
        password=hash_password(user_mock_data.password),
        is_active=True,
        is_authenticated=True,
        role="Admin"  # Make sure this user is an Admin
    )
    
    # 2) Add the newly created admin user in the DB:
    db_session.add(admin_user)
    db_session.commit()

    # 3) Construct the login fields to log in the admin:
    login_field = LoginFields(
        email="admin@example.com",
        password="StrongPassword123$"
    )

    # 4) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 5) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 6) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 7) Attempt to modify the username of user with ID = 15:
    new_fields = UpdateUserDetailsField(
        user_id=15,
        new_username="Alain",
        new_user_role="user"
    )

    # 8) Send the request to the appropriate endpoint in the backend:
    response = test_client.put(
        "/users/update-user-details",
        json={
            "user_id": new_fields.user_id,
            "new_username": new_fields.new_username,
            "new_user_role": new_fields.new_user_role
        },
        headers=headers  # Include the headers with the Authorization token
    )

    # 9) Assess the status code of the request:
    assert response.status_code == 200

    # 10) Assess that the username has been changed:
    user_db = db_session.query(User).filter_by(email=user_mock_data.email).first()
    assert user_db.username == "Alain"



# ============================================================================================================
# Test 17: Test update user's detail route with an admin account (only role is modified)
@pytest.mark.asyncio
async def test_update_users_detail_route_admin_new_role(test_client, db_session):
    """ Test update user's detail route with an admin account (only username is modified) """
   
    # 1) Set the login credentials for the admin
    login_field = LoginFields(
        email="admin@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 6) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 7) Attempt to modify the username of user with ID = 15:
    new_fields = UpdateUserDetailsField(
        user_id=15,
        new_username="Jake",
        new_user_role="Admin"
    )

    # 8) Send the request to the appropriate endpoint in the backend:
    response = test_client.put(
        "/users/update-user-details",
        json={
            "user_id": new_fields.user_id,
            "new_username": new_fields.new_username,
            "new_user_role": new_fields.new_user_role
        },
        headers=headers  # Include the headers with the Authorization token
    )

    # 9) Assess the status code of the request:
    assert response.status_code == 200

    # 10) Assess that the username has been changed:
    user_db = db_session.query(User).filter_by(email=user_mock_data.email).first()
    assert user_db.role == "Admin"

    # 11) Reset modifications:
    new_fields = UpdateUserDetailsField(
        user_id=15,
        new_username="Jake",
        new_user_role="user"
    )
    response = test_client.put(
        "/users/update-user-details",
        json={
            "user_id": new_fields.user_id,
            "new_username": new_fields.new_username,
            "new_user_role": new_fields.new_user_role
        },
        headers=headers
    )




# ============================================================================================================
# Test 18: Test update user's detail route with an admin account (username and role is modified)
@pytest.mark.asyncio
async def test_update_users_detail_route_admin_new_role_and_username(test_client, db_session):
    """ Test update user's detail route with an admin account (only username is modified) """
   
    # 1) Set the login credentials for the admin
    login_field = LoginFields(
        email="admin@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 6) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 7) Attempt to modify the username of user with ID = 15:
    new_fields = UpdateUserDetailsField(
        user_id=15,
        new_username="Eric",
        new_user_role="Admin"
    )

    # 8) Send the request to the appropriate endpoint in the backend:
    response = test_client.put(
        "/users/update-user-details",
        json={
            "user_id": new_fields.user_id,
            "new_username": new_fields.new_username,
            "new_user_role": new_fields.new_user_role
        },
        headers=headers  # Include the headers with the Authorization token
    )

    # 9) Assess the status code of the request:
    assert response.status_code == 200

    # 10) Assess that the username has been changed:
    user_db = db_session.query(User).filter_by(email=user_mock_data.email).first()
    assert user_db.username == "Eric"
    assert user_db.role == "Admin"


    # 11) Reset modifications:
    new_fields = UpdateUserDetailsField(
        user_id=15,
        new_username="Jake",
        new_user_role="user"
    )
    response = test_client.put(
        "/users/update-user-details",
        json={
            "user_id": new_fields.user_id,
            "new_username": new_fields.new_username,
            "new_user_role": new_fields.new_user_role
        },
        headers=headers
    )




# ============================================================================================================
# Test 19: Test update user's detail route with an user account (username and role is modified):
@pytest.mark.asyncio
async def test_update_users_detail_route_user_new_role_and_username(test_client, db_session):
    """ Test update user's detail route with an admin account (only username is modified) """
   
    # 1) Set the login credentials for the admin
    login_credentials = LoginFields(
        email="testuse3@example.com",
        password="NewStrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_credentials.email,
        'password': login_credentials.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 6) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 7) Attempt to modify the username of user with ID = 15:
    new_fields = UpdateUserDetailsField(
        user_id=1,
        new_username="Jeff",
        new_user_role="Admin"
    )

    # 8) Send the request to the appropriate endpoint in the backend:
    response = test_client.put(
        "/users/update-user-details",
        json={
            "user_id": new_fields.user_id,
            "new_username": new_fields.new_username,
            "new_user_role": new_fields.new_user_role
        },
        headers=headers  # Include the headers with the Authorization token
    )

    # 9) Assess the status code of the request:
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "Not an Admin thus not authorized."


    # 11) Reset modifications:
    new_fields = UpdateUserDetailsField(
        user_id=15,
        new_username="Jake",
        new_user_role="user"
    )
    response = test_client.put(
        "/users/update-user-details",
        json={
            "user_id": new_fields.user_id,
            "new_username": new_fields.new_username,
            "new_user_role": new_fields.new_user_role
        },
        headers=headers
    )


# ============================================================================================================
# Test 20: Test the block user account route with an admin account:
@pytest.mark.asyncio
async def test_block_account_admin(test_client, db_session):
    """Test the block user account route with an admin account"""
    # 1) Set the login credentials for the admin
    login_field = LoginFields(
        email="admin@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 4) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 5) Set the freezeaccountfield:
    account_to_freeze = FreezeAccountFields(
        user_id=15
    )

    # 7) Send the request to block the account in the appropriate endpoint:
    response = test_client.put(
        "/users/block-user-account",
        json={
            'user_id': account_to_freeze.user_id
        },
        headers=headers
    )

    # 8) Assess the response:
    assert response.status_code == 200
    user_db = db_session.query(User).filter_by(id=15).first()
    assert user_db.is_active == False

    

# ============================================================================================================
# Test 21: Test the unblock user account route with an admin account:
@pytest.mark.asyncio
async def test_unblock_account_admin(test_client, db_session):
    """Test the unblock user account route with an admin account"""
    # 1) Set the login credentials for the admin
    login_field = LoginFields(
        email="admin@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 4) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 5) Set the freezeaccountfield:
    account_to_freeze = FreezeAccountFields(
        user_id=15
    )

    # 7) Send the request to block the account in the appropriate endpoint:
    response = test_client.put(
        "/users/unblock-user-account",
        json={
            'user_id': account_to_freeze.user_id
        },
        headers=headers
    )

    # 8) Assess the response:
    assert response.status_code == 200
    user_db = db_session.query(User).filter_by(id=15).first()
    assert user_db.is_active == True

    


# ============================================================================================================
# Test 22: Test the block user account route with a user account:
@pytest.mark.asyncio
async def test_block_account_user(test_client, db_session):
    """Test the block user account route with a user account"""
    # 1) Set the login credentials for the admin
    login_field = LoginFields(
        email=user_mock_data.email,
        password=user_mock_data.password
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 4) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 5) Set the freezeaccountfield:
    account_to_freeze = FreezeAccountFields(
        user_id=15
    )

    # 7) Send the request to block the account in the appropriate endpoint:
    response = test_client.put(
        "/users/block-user-account",
        json={
            'user_id': account_to_freeze.user_id
        },
        headers=headers
    )

    # 8) Assess the response:
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "Not an Admin thus not authorized."

    

# ============================================================================================================
# Test 23: Test the block user account route with a user account:
@pytest.mark.asyncio
async def test_unblock_account_user(test_client, db_session):
    """Test the unblock user account route with a user account"""
    # 1) Set the login credentials for the admin
    login_field = LoginFields(
        email=user_mock_data.email,
        password=user_mock_data.password
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']

    # 4) Set up the Authorization header with the access token:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 5) Set the freezeaccountfield:
    account_to_freeze = FreezeAccountFields(
        user_id=15
    )

    # 7) Send the request to block the account in the appropriate endpoint:
    response = test_client.put(
        "/users/unblock-user-account",
        json={
            'user_id': account_to_freeze.user_id
        },
        headers=headers
    )

    # 8) Assess the response:
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "Not an Admin thus not authorized."



# ============================================================================================================
# Test 24: Test the visualize stock clusters route:
@pytest.mark.asyncio
async def test_kmean_route(test_client, db_session):
    """Test the visualize stock clusters route """
    # 1) Set the login credentials:
    login_field = LoginFields(
        email="admin@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

   # 5) Perform KMeans to generate stock clusters:
    response = test_client.get("/visualze/kmean-cluster", headers=headers)

    # 6) Assert the response status code is 200:
    assert response.status_code == 200
    # INFO: Result returned is a double encoded JSON obj:
    # 7) Extract the JSON content from the KMeans clustering response:
    result_json_str = response.text  # Use .text to get the raw response body => return a string looking like json obj
    # 8) First, convert the string to a proper JSON object (it may be double-encoded):
    outer_json = json.loads(result_json_str)
    # 9) If the result is still a string, parse it again:
    if isinstance(outer_json, str):
        result_dict = json.loads(outer_json)  # Converts the second layer JSON string to a dictionary
    else:
        result_dict = outer_json  # In case it was already a dictionary (just a precaution)

    # 10) Ensure the response JSON is a dictionary:
    assert isinstance(result_dict, dict), "Response JSON is not a dictionary"

    expected_keys = ['Ticker', 'Avr Annual Return', 'Avr Annual Volatility', 'Cluster']

    # 11) Check if each item in the JSON contains the required keys:
    for item_key, item_value in result_dict.items():
        assert all(key in item_value for key in expected_keys), f"Missing expected keys in item {item_key}"

# ============================================================================================================
# Test 25: Test the predict next closing price trend route:
@pytest.mark.asyncio
async def test_predict_next_closing_price_trend_route(test_client, db_session):
    """Test the predict next closing price trend route """
        # 1) Set the login credentials:
    login_field = LoginFields(
        email="admin@example.com",
        password="StrongPassword123$"
    )

    # 2) Perform the login request to obtain a JWT token:
    response = test_client.post("/auth/login", json={
        'email': login_field.email,
        'password': login_field.password
    })

    # 3) Assert the login response is successful:
    assert response.status_code == 200
    login_response_data = response.json()
    access_token = login_response_data['access_token']
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

# 4) Perform the price prediction:
    ticker = 'AAPL'
    response = test_client.get(f"/predict_next_closing_trend/predict_closing_price_trend?ticker={ticker}", headers=headers)

    # 5) Assess if the response status code is 200:
    assert response.status_code == 200

    # 6) (Optional) Verify the content of the response if required:
    response_json = response.json()
    assert "result" in response_json, "Missing 'result' key in the response JSON."
    assert response_json["result"] in [0, 1], "The prediction result should be either 0 (Lower) or 1 (Higher)."