from datetime import datetime, timedelta, timezone
# Library used to display logging messages to help developpers to diagnose issues or to record events in the app.
import logging
# Library used to generate secure random nbr for cryptographic use.
import secrets
# Library used to to encode and decode JWT token.
from jose import JWTError
import jwt
# Library used for encoding data in ASCII char using Base64 encoding.
import base64

from fastapi import Security, status
# Library used for making HTTP requests.
from requests import Session
# Library used to retrieve and validate bearer tokends from HTTP requests.
from fastapi.security import OAuth2PasswordBearer
# Library used for password hashing.
from passlib.context import CryptContext
# Fastapi Depends allows to declare dependencies in API endpoints.
# Fastapi HTTPException allows to return errors w/ specific HTTP status codes and custom error messages.
from fastapi import Depends, HTTPException
# JoinLoad enables to reduce the nbr of queries to improve performance when accessing obj.
from sqlalchemy.orm import joinedload

from src.Configuration.settings import get_settings
from src.Configuration.database import get_db
from src.Models.TokenModel import Token
from src.Models.UserModel import User



# Get the all settings defined in src/Configuration/settings:
settings = get_settings()

# Initialize password hashing context from passlib library:
# Purpose: Specifies the password hashing scheme to be used: bcrypt = password hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define OAuth2 password beareer scheme from fastapi security library:
# Purpose: Define a bearer token authentication scheme for securing endpoints that require authentication
# "/autg/login" specifies the endpoint where clients can request an access token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Define a lost of special characters that must be included in the password for enhanced security:
SPECIAL_CHARACTERS = ['@', '#', '%', '=', ':', '?', '.', '/', '|', '~', '>', '<', '$', '!', '£']


# Purpose: Hash a password to secure it:
def hash_password(password: str) -> str:
  return pwd_context.hash(password)


# Purpose: Verify the hashed password against the plain password:
def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


# Assess if the password meets the strength requirements:
def is_password_strong_enough(password: str) -> bool:
  # 1st req: length(password) > 8:
  if len(password) < 8:
    return False
  # 2nd red: Nbr upper char >= 1:
  if not any(char.isupper() for char in password):
    return False
  # 3rd red: Nbr lower char >= 1:
  if not any(char.islower() for char in password):
    return False
  # 4th req: Nbr digits char >= 1:
  if not any(char.isdigit() for char in password):
    return False
  # 5th req: Nbr of special char >= 1
  if not any(char in SPECIAL_CHARACTERS for char in password):
    return False
  return True


# Purpose: Encode a string using base 85:
def str_encode(string: str) -> str:
    return base64.b85encode(string.encode('ascii')).decode('ascii')


# Purpose: Decode base 85 string:
def str_decode(string: str) -> str:
    return base64.b85decode(string.encode('ascii')).decode('ascii')


# Purpose: Decode a JWT token and get the payload:
def get_token_payload(token: str, secret: str, algo: str):
    logging.info(f"Token received for decoding: {token}")
    try:
        payload = jwt.decode(token, secret, algorithms=algo)
    # Case where JWT has expired:
    except jwt.ExpiredSignatureError:
        logging.warning("JWT token has expired.")
        payload = None
    # Case where Invalid JWT:
    except jwt.InvalidTokenError as jwt_exec:
        logging.error(f"JWT Error: {str(jwt_exec)}")
        payload = None
    return payload


# Purpose: Generate a random and unic string of specified length using secret module for security purpose:
def unique_string(byte: int=8) -> str:
   return secrets.token_urlsafe(byte)


# Purpose: Generate a JWT token to protect the API:
# payload: dicionary containing the data that I want to encore into the JWT (User ID, Roles ...)
# secrets: secret key used to sign the JWT token defined in the .env file
# algo: Algorith used for signing the JWT token defined in the .env file
# expiry: specifies the expiration time of the JWT
def generate_token(payload: dict, secret: str, algo: str, expiry: timedelta):
    # 1) Compute the expiry time of the token:
    expire = datetime.now(timezone.utc) + expiry
    # 2) Update the payload: Add the computed expire to the payload dictionnary
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm=algo)


# Purpose: Retrieve a user associated to JWT token from the DB
# token: JWT token
# db: Database session
async def get_token_user(token: str, db):
    # 1) Decode the JWT token by using JWT secret and algorithm
    payload = get_token_payload(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    if payload:
        # 2) Extract the payload data:
        # 2.1) Retrieve the user token ID 
        user_token_id = str_decode(payload.get('r'))
        # 2.2) Retrieve the User ID
        user_id = str_decode(payload.get('sub'))
        # 2.3) Retrieve the access jey
        access_key = payload.get('a')
        # 3) Construct a query to fetch the Token obj from the database based on: access_key, user_token_id, user_id.
        user_token = db.query(Token).options(joinedload(Token.user)).filter(Token.access_key == access_key,
                                                 Token.id == user_token_id,
                                                 Token.user_id == user_id,
                                                 Token.expires_at > datetime.now(timezone.utc)
                                                 ).first()
        if user_token:
            return user_token.user
    return None


# Purpose: return a user from the database given its email:
# email: email addrress of the user that we want to load from the database
# db: database session
async def load_user(email: str, db: Session) -> User:
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            logging.info(f"User Found, Email: {email}")
        else:
            logging.info(f"User Not Found, Email: {email}")
    except Exception as user_exec:
        logging.exception(f"An error occurred while fetching the user, Email: {email}")
        user = None
    return user


# Purpose: Retrieve a user from a JWT token:
# token: JWT token used for authentication
# Dependency inj: ensures that before get_current_user is executed, it first validates and extracts the JWT token from the request using oauth2_scheme.
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = await get_token_user(token=token, db=db)
    if user:
      return user
    raise HTTPException(status_code=401, detail="Not authorised.")
