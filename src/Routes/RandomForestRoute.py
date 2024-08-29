from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from requests import Session

# Imports from Configurations:
from src.Configuration.database import get_db
from src.Configuration.security import get_current_user
# Imports from Models:
from src.Models.UserModel import User
# Imports from Services:
from src.Services import RandomForesstService


random_forest_router = APIRouter(
  prefix='/predict_next_closing_trend',
  tags=['Predict_next_closing_trend'],
  responses={404: {'description': 'Not found'}}
)


# Purpose: Generate prediction using the Random Forest model:
@random_forest_router.get('/predict_closing_price_trend', status_code=status.HTTP_200_OK)
async def get_prediction(ticker: str, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  if not current_user:
    raise HTTPException(status_code=401, detail="Not authorized.")
  if not current_user.role == "Admin":
    raise HTTPException(status_code=401, detail="Not an admin thus not authorized.")
  prediction = await RandomForesstService.orchestrate_random_forest(ticker)
  return JSONResponse({"result": prediction})
