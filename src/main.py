# # src/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# # Import from Configuration:
# from src.Configuration.database import Base, engine
# # Import Routes:
# from src.Routes.UserRoutes import user_router
# from src.Routes.AuthRoutes import auth_router
# from src.Routes.RoleRoutes import role_router
# from src.Routes.DataRoutes import data_router
# from src.Routes.RandomForestRoute import random_forest_router
# from src.Routes.KMeanRoute import kmean_router;


# # Create FastAPI application
# app = FastAPI()



# # Define the origins that should be allowed to make cross-origin requests
# origins = [
#     "http://localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers from UserRoute
# app.include_router(user_router)
# app.include_router(auth_router)
# app.include_router(role_router)
# app.include_router(data_router)
# app.include_router(random_forest_router)
# app.include_router(kmean_router)

# # Create all database tables
# Base.metadata.create_all(bind=engine)


# @app.get("/")
# def read_root():
#     return {"Hello": "World!"}



# =========================================================


# # src/main.py
# import os
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# # Import from Configuration:
# from src.Configuration.database import Base

# # Import Routes:
# from src.Routes.UserRoutes import user_router
# from src.Routes.AuthRoutes import auth_router
# from src.Routes.RoleRoutes import role_router
# from src.Routes.DataRoutes import data_router
# from src.Routes.RandomForestRoute import random_forest_router
# from src.Routes.KMeanRoute import kmean_router

# # Determine the database URL based on the environment
# if os.getenv("TESTING"):
#     DATABASE_URL = "sqlite:///:memory:"  # For in-memory testing
# else:
#     DATABASE_URL = "postgresql://postgres:mysecretpassword@db:5432/mydatabase"

# # Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL)

# # Create FastAPI application
# app = FastAPI()

# # Define the origins that should be allowed to make cross-origin requests
# origins = [
#     "http://localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers from UserRoute
# app.include_router(user_router)
# app.include_router(auth_router)
# app.include_router(role_router)
# app.include_router(data_router)
# app.include_router(random_forest_router)
# app.include_router(kmean_router)

# # Create all database tables
# Base.metadata.create_all(bind=engine)

# @app.get("/")
# def read_root():
#     return {"Hello": "World!"}



# ==================================================

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.Configuration.settings import get_settings
from src.Configuration.database import Base

# Import Routes:
from src.Routes.UserRoutes import user_router
from src.Routes.AuthRoutes import auth_router
from src.Routes.RoleRoutes import role_router
from src.Routes.DataRoutes import data_router
from src.Routes.RandomForestRoute import random_forest_router
from src.Routes.KMeanRoute import kmean_router

# Get settings
settings = get_settings()

# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Create FastAPI application
app = FastAPI()

# Define the origins that should be allowed to make cross-origin requests
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from UserRoute
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(data_router)
app.include_router(random_forest_router)
app.include_router(kmean_router)

# Create all database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World!"}
