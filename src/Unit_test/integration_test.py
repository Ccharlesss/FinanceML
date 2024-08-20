# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from fastapi.testclient import TestClient

# from src.Configuration.settings import get_settings
# from src.Configuration.database import Base  # Ensure this import is correct
# from src.main import app
# from src.Models.UserModel import User

# # Import your mock data and other necessary modules
# from src.Schemas.UserSchemas import UserCreate

# from mongomock_motor import AsyncMongoMockClient



# mock_data = UserCreate(
#     username="testuser",
#     email="testuser@example.com",
#     password="StrongPassword123$"
# )

# settings = get_settings()
# print(f"DATABASE_URL: {settings.DATABASE_URL}")


# # Mock the db
# app.mongodb = AsyncMongoMockClient()[settings.DB_NAME]



# @pytest.mark.asyncio
# async def test_create_account_route_with_strong_password(client, db_session):
#     background_tasks = BackgroundTasks()
    
#     # Call the function directly
#     response = await create_user_account(mock_data, background_tasks, db_session)
    
#     # 1) If `create_user_account` returns a User object, you may need to adjust the assertions accordingly.
#     assert isinstance(response, User)
    
#     # 2) You can also assert that the `User` object has the expected data.
#     assert response.username == mock_data.username
#     assert response.email == mock_data.email
    
#     # 3) Verify the user was correctly added into the database:
#     user_db = db_session.query(User).filter_by(email=mock_data.email).first()
#     assert user_db is not None
#     assert user_db.username == mock_data.username
#     assert user_db.email == mock_data.email
#     assert user_db.role == 'user'




# ============================================================================================================
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from src.main import app  # Adjust this import to your actual FastAPI app path
from src.Configuration.database import get_db, Base  # Adjust this import to your actual SQLAlchemy config
from src.Models.UserModel import User  # Adjust this import to your actual User model path
from src.Schemas.UserSchemas import UserCreate  # Adjust this import to your actual UserCreate schema path

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
    
@pytest.mark.asyncio
async def test_create_account_route_with_strong_password(test_client, db_session):
    """Test creating a new account with a strong password."""
    # Define mock data
    mock_data = UserCreate(
        username="testuser",
        email="testuser@example.com",
        password="StrongPassword123$"
    )

    # Perform the request
    response = test_client.post("/users/signup", json={
        'username': mock_data.username,
        'email': mock_data.email,
        'password': mock_data.password
    })

    # Print the response details for debugging
    response_data = response.json()
    print(response_data)  # This will help you see the actual structure

    # Check that the response status code is as expected
    assert response.status_code == 201

    # Adjust assertions to match the actual response structure
    assert 'username' in response_data
    assert response_data['username'] == mock_data.username
    assert response_data['email'] == mock_data.email

    # Validate the user has been created in the database
    user_db = db_session.query(User).filter_by(email=mock_data.email).first()
    assert user_db is not None
    assert user_db.username == mock_data.username
    assert user_db.email == mock_data.email
    assert user_db.role == 'user'