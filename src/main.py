# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import from Configuration:
from src.Configuration.database import Base, engine
# Import Routes:
from src.Routes.UserRoutes import user_router
from src.Routes.AuthRoutes import auth_router
from src.Routes.RoleRoutes import role_router
from src.Routes.DataRoutes import data_router
from src.Routes.RandomForestRoute import random_forest_router
from src.Routes.KMeanRoute import kmean_router;


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
