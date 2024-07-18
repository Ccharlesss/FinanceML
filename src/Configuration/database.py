import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Retrieve DB_URL from environment variables
DATABASE_URL = os.getenv("DB_URL")

# Ensure DATABASE_URL is properly populated:
if DATABASE_URL is None:
    raise ValueError("No DATABASE_URL found in environment variables")


# Create an SQLAlchemy 'Engine' obj which represents the interface to the database:
# Purpose: Connections to the db and executes SQL commands:
engine = create_engine(DATABASE_URL)



# Create a 'SessionLocal' factory
# Purpose: Enable to interact and perform CRUD operations in the database
# autocommit=False: Ensures that changes are not automatically commited to db
# autoflush=False: prevents SQLAlchemy from automatically issuing SQL queries to refresh objects
# bind=engine: specifies that the sessionmaker should use engine obj to connect to the database 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base serves as base class from which your ORM (Object-Relational Mapping) models will inherit.
# Purpose: Enabkes SQLAlchemy to map python obj to the database tables
Base = declarative_base()


# Dependency to get a session in your FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
