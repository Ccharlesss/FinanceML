# settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from urllib.parse import quote_plus

# ===================================================================================================================================
# Purpose of Settings.py file: manage configuration settings for your FastAPI application in a clean, flexible, and secure way.
# ===================================================================================================================================


# Define the path to the .env file:
env_path = Path(".") / ".env"
# Load the .env file w/ all settings:
load_dotenv(dotenv_path=env_path)


# ===================================================================================================================================
# Purpose of Settings class: Store configuration variables for our application and database.
# ===================================================================================================================================
class Settings(BaseSettings):
    # Web app settings:
    APP_NAME: str = "My FastAPI App"
    DEBUG: bool = False


    # PostgreSQL database configuration:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "mydatabase")
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Frontend host:
    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "http://localhost:3000")

    #Mail Configuration:
    # MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    # MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    # MAIL_FROM: str = os.getenv("MAIL_FROM")
    # MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    # MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    # MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME")
    # MAIL_TLS: bool = os.getenv("MAIL_TLS", "false").lower() == "true"  # Adjusted for TLS support
    # MAIL_USE_CREDENTIALS: bool = os.getenv("MAIL_USE_CREDENTIALS", "false").lower() == "true"
    # MAIL_VALIDATE_CERTS: bool = os.getenv("MAIL_VALIDATE_CERTS", "false").lower() == "true"



    # JWT Secret Key:
    JWT_SECRET: str = os.getenv("JWT_SECRET", "649fb93ef34e4fdf4187709c84d643dd61ce730d91856418fdcf563f895ea40f")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 1440))

    # Secret Key for app security:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "W1-aeU3M_rk3kZ8XsQG6QFh3h-RMVPaNpKJb3On5wYQ")



    # Database URL (constructed dynamically) using environment variables defined in the Settings class.
    # @property decorator in Python allows you to define a method in a class that can be accessed like an attribute.
    # This enables DATABASE_URL to be used like an attribute of Settings
    # quote_plus from the urllib.parse module is used to encode special characters in the username and password to ensure they are valid in URLs
    @property
    def DATABASE_URL(self) -> str:
        return (
            # User Information encoding
            f"postgresql://{quote_plus(self.POSTGRES_USER)}:"
            # Host and Port encoding
            f"{quote_plus(self.POSTGRES_PASSWORD)}@"
            # Database Name encoding
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

# ===================================================================================================================================
# Purpose: Encoding payload of JWT token and Decoding it
# secret key is used to sign and verify JSON Web Tokens (JWTs)
# When issuing a JWT, the server signs the payload with the secret key.
# When a JWT is received, the server uses the same key to verify its signature.
# ===================================================================================================================================
SECRET_KEY: str = os.getenv("SECRET_KEY", "default_fallback_secret_key")


# ===================================================================================================================================
# Purpose of Config inner class: Informs Pydantic’s BaseSettings how to load and parse environment variables:
# ===================================================================================================================================
class Config:
  # Set the environment variable prefix if needed (optional): Here no prefix required => looks for env var defined in Settings class
  env_prefix = ""
  # Load variables from .env file
  env_file = env_path
  # Specifies the encoding used to read the .env file.
  env_file_encoding = 'utf-8'


# ===================================================================================================================================
# Purpose: provides a cached, singleton instance of the Settings class, ensuring efficient access to configuration settings throughout the app
# ===================================================================================================================================
# LRU Cache: LRU stands for "Least Recently Used". The cache keeps the most recently used results and discards the least recently used ones 
# Advantage: Improves performance by avoiding repeated initialization of settings, ensuring that settings are loaded once and reused.
  
# Mecanism: store the result of a function call based on its input parameters.
# Mecanism: get_settings() is a function that returns an instance of the Settings class.
# Mecanism: @lru_cache() is applied to get_settings(), meaning it caches the return value of get_settings()
# Mecanism: When first called, initializes and stores a new instance of Settings class and return it
# Mecanism: Subsequent calls: Instead of creating new instance, checks if function has been called w/ same arg as before
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Example usage
# settings = get_settings()
# print(settings.DATABASE_URL)
