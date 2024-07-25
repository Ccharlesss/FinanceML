from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

# Imports from Services:
from src.Services import StoreFinancialDataServices
# Imports from Context:
from src.Context.StockContext import SP500


data_router = APIRouter(
  prefix='/data',
  tags=['Data'],
  responses={404: {'description': 'Not found'}}
)


### Gather all financial data and store in into a CSV file:
@data_router.get('/fetch&store_financial_data', status_code=status.HTTP_200_OK)
async def gather_data():
  success = await StoreFinancialDataServices.store_data_into_cvs(SP500)
  if success:
    return JSONResponse({"message":"Data have been successfully stored into a CSV file"})
  else:
    return JSONResponse({"message": "Failed to store data into CSV file"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
  


### Gather the missing up-to-date financial data and store it into the CSV file:
@data_router.get('/get-uptodate-data', status_code=status.HTTP_200_OK)
async def update_csv():
    success = await StoreFinancialDataServices.get_missing_recent_data(SP500)
    if success:
        return JSONResponse({"message": "Data has been successfully updated and stored in the CSV file"})
    else:
        return JSONResponse({"message": "Failed to update and store data in the CSV file"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
