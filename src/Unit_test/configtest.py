import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.Configuration.settings import get_settings
from src.main import app  # Import your FastAPI app
from src.Models.UserModel import User
from src.Models.TokenModel import Token
from src.Configuration.database import Base

# Test user details
USER_NAME = "Romain Charles"
USER_EMAIL = "testemail@gmail.com"
USER_PASSWORD = "Testpassword64$"

# Get settings and database URL
settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to set up the FastAPI app and database
@pytest.fixture(scope="function")
def app_test() -> FastAPI:  # type: ignore
    """Fixture to set up and tear down the FastAPI app for tests."""
    
    # Create the database tables before tests
    Base.metadata.create_all(bind=engine)
    
    # Yield the FastAPI app instance
    yield app

    # Drop the database tables after tests
    Base.metadata.drop_all(bind=engine)

# Fixture for creating a TestClient
@pytest.fixture(scope="function")
def client(app_test, db_session):
    """Provides a TestClient with the FastAPI app."""
    with TestClient(app_test) as client:
        yield client

# Fixture to provide a session for each test
@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create the session for the test
    db = SessionLocal()

    yield db  # This is where the testing happens

    # Roll back the transaction and close the connection
    transaction.rollback()
    connection.close()
    db.close()  # Ensure the session is closed
