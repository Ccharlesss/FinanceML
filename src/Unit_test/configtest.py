import os
from typing import Generator
from httpx import AsyncClient
import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import os

# Load environment variables from .env.test file
load_dotenv('.env.test')

from src.main import app
from src.Configuration.email import fm
from src.Configuration.database import Base, get_db
from src.Configuration.security import hash_password
from src.Models.UserModel import User
from src.Controllers.UserController import _generate_tokens

USER_NAME = "Romain Charles"
USER_EMAIL = "testemail@gmail.com"
USER_PASSWORD = "Testpassword64$"



## ========================================================================================================
##                                           CONFIGURE TEST DB
DATABASE_URL_TEST = "sqlite:///:memory:"
# 1) Initialize the test db: 
# create_engine: Creates a new SQLAlchemy Engine instance to interact with the database.
# connect_args={"check_same_thread": False}: Allows SQLite to be used across different threads.
# poolclass=StaticPool: Ensures a single connection is used throughout, which is helpful for tests.
engine = create_engine(DATABASE_URL_TEST, connect_args={"check_same_thread": False}, poolclass=StaticPool)
# 2) Create a test session:
# Sessionmaker: Factory for creating new SQLAlchemy Session objects.
# autocommit=False: Disables automatic committing of transactions.
# autoflush=False: Prevents automatic flushing of changes to the database.
# bind=engine: Binds the session to the test database engine created above.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the dependency override for testing
app.dependency_overrides[get_db] = override_get_db




@pytest.fixture(scope="function")
def test_session() -> Generator:
    """Provides a database session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope='function')
def app_test():
    """Sets up and tears down the database tables for each test."""
    # Create an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app.dependency_overrides[get_db] = lambda: SessionLocal()
    
    yield app  # This will run the test

    Base.metadata.drop_all(bind=engine)



@pytest.fixture(scope="function")
async def client(app_test, test_session):
    """Provides an AsyncClient with the FastAPI app and a valid token."""
    # Ensure emails are not sent during tests
    fm.config.SUPPRESS_SEND = True

    # Create a test user and generate tokens
    user = User(username=USER_NAME, email=USER_EMAIL, password=hash_password(USER_PASSWORD))
    test_session.add(user)
    test_session.commit()
    tokens = _generate_tokens(user, test_session)

    # Create the test client
    async with AsyncClient(app=app_test, base_url="http://test") as client:
        client.headers['Authorization'] = f"Bearer {tokens['access_token']}"
        yield client















