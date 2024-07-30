from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from requests import Session

# Imports from Configurations:
from src.Configuration.database import get_db
from src.Configuration.security import get_current_user
# Imports from Models:
from src.Models.UserModel import User
# Imports from Serbices:
from src.Services import KMeanService


kmean_router = APIRouter(
  prefix='/visualze',
  tags=['/Visualize'],
  responses={404: {'description': 'Not found'}}
)

### Generate K-mean cluster plot ###
@kmean_router.get('/kmean-cluster', status_code=status.HTTP_200_OK)
async def get_kmean_plot(session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  if not current_user:
    raise HTTPException(status_code=401, detail="Not authorized.")
  if not current_user.role == "Admin":
    raise HTTPException(status_code=401, detail="Not an admin thus not authorized.")
  await KMeanService.orchestrate_kmean_and_plot()
  return JSONResponse({"message": "KMean and the plot was performed successfully."})