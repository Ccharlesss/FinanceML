# src/main.py
from fastapi import FastAPI
# Import from Configuration:
from src.Configuration.database import Base, engine
# Import Routes:
from src.Routes.UserRoutes import user_router
from src.Routes.AuthRoutes import auth_router, notyet_login_router
from src.Routes.RoleRoutes import role_router

# Create FastAPI application
app = FastAPI()

# Include routers from UserRoute
app.include_router(user_router)
app.include_router(notyet_login_router)
app.include_router(auth_router)
app.include_router(role_router)

# Create all database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Hello": "World!"}
