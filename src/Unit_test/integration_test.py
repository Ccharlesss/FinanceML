# Imports required for the testing library:
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
# Imports from the test configuration file:
from src.Unit_test.configtest import client, db_session, app_test
# Imports from Models:
from src.Models.UserModel import User
# Imports from Schemas:
from src.Schemas.UserSchemas import UserCreate


mock_data = UserCreate(
    username="testuser",
    email="testuser@example.com",
    password="StrongPassword123$"
)


# ===================================================================================================================
# Test 1: Create a user account with a strong password:
@pytest.mark.asyncio
async def test_create_account_route_with_strong_password(client, db_session):
  # 1) Send POST request to the /users/signup endpoint:
  response = client.post('/users/signup', json=mock_data.model_dump())
  # 2) Assert that the response status code is 201 Created:
  assert response.status_code == 201
  # 3) Assert that the response contains the expected data
  response_data = response.json()
  assert response_data['message'] == "Account created successfully"
  assert response_data['user']['username'] == mock_data['username']
  assert response_data['user']['email'] == mock_data['email']
  # 4) Verify the user was correctly added into the database:
  user_db = db_session.query(User).filter_by(email=mock_data.email).first()
  assert user_db is not None
  assert user_db.username == mock_data.username
  assert user_db.email == mock_data.email
  assert user_db.role == 'user'

