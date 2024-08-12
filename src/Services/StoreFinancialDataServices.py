import io
import os
import aiofiles
from fastapi import HTTPException
import yfinance as yf
import pandas as pd
from venv import logger
from datetime import datetime, timedelta

# Import the path where financial data will be stored into a CSV:
from src.Context.StockContext import CSV_FILE_PATH
# Import the path where the file that stores the date when the CSV was updated:
from src.Context.StockContext import DATE_FILE_PATH





# Write the current date when CSV file was modified in the format YYYY-MM-DD:
async def write_date_when_retrieved() -> bool:
  # 1) Get the latest date when financial data was gathered:
  todays_date = datetime.now().strftime("%Y-%m-%d")
  # 2) Attempt to write the date into a txt file:
  try:
    with open(DATE_FILE_PATH, "a") as file:
      # file.write(f"{todays_date}\n")
      file.write(f"{todays_date}\n")
      logger.info(f"{todays_date} was successfully added into {DATE_FILE_PATH}")
      return True
  
  except Exception as e:
    logger.error(f"failed to store the latest date {DATE_FILE_PATH}: {e}")
    return False
  



# Retrieve the latest date with of financial data at the end of a txt file:
async def get_latest_date_of_financial_data() -> str:
  # 1) Assess whether the file is empty or not
  try:
    # 1.1) Get the size of the txt file:
    file_size = os.path.getsize(DATE_FILE_PATH)
    # 1.2) of file_size == 0 => file is empty:
    if file_size == 0:
      logger.info(f"No dates are stored into {DATE_FILE_PATH}")
      print(f"No dates are stored into {DATE_FILE_PATH}")
      return None
   
    # 1.2) If file exist and isn't empty => extract lastest date:
    else:
      with open(DATE_FILE_PATH, 'r') as file:
        # 1.3) Read all lines in the txt file, extract date in last line:
          lines = file.readlines()
          if lines:
            latest_date = lines[-1].strip()  # Get the last line and remove any extra whitespace
            return latest_date
          else:
            logger.info(f"No dates are stored in {DATE_FILE_PATH}")
            print(f"No dates are stored in {DATE_FILE_PATH}")
            return None
  except FileNotFoundError as e:
    logger.error(f"error: {e}")
    raise HTTPException(status_code=500, detail=f"Failed to retrieve the latest date: {str(e)}")





# Async function that converts a DataFrame into a CSV file:
async def convert_df_to_csv(df: pd.DataFrame) -> bool:
  # 1) try to convert the DataFrame into a CSV file:
  try:
    df.to_csv(CSV_FILE_PATH, index=True)
    logger.info(f"Financial data was successfully stored in {CSV_FILE_PATH}")
    return True
  except Exception as e:
    logger.error(f"Failed to store data into CSV file: {e}")
    return False
  



# Async function that gathers daily financial data to store it in a CSV file:
async def store_data_into_cvs(tickers: list) -> bool:
  # 1) Initialize an empty dataframe to store all the financial data:
  final_df = pd.DataFrame()
  # 2) Iterate through all ticker in tickers:
  for ticker in tickers:
    # 2.1) Gather the stock's financial data for past 5y:
    stock = yf.Ticker(ticker)
    stock_df = stock.history(period="5y")
    # 2.2) Assess if there df is empty => don't use this stock
    if not stock_df.empty:
      # 2.3) Add the stock's ticker symbol as a column:
      stock_df['Ticker'] = ticker
      # 2.4) append stock_df into the dataframe that will be converted into a CSV file:
      final_df = pd.concat([final_df, stock_df])
    else:
       logger.info(f"No financial data could be gathered for the following stock {ticker}")

  # 3) Assess whether the final dataframe is empty:
  if final_df.empty:
    logger.error(f"Error: The dataframe used to store all stock's financial result is empty")
    return False
  
  # 4) If final DF not empty, attempt to convert it in CVS
  result = await convert_df_to_csv(final_df)
  # 5) If operation was successful attempt to write the date where data ends_
  if result:
     return await write_date_when_retrieved()
  return False






# Async function that gathers daily financial data to store it in a CSV file:
# async def store_data_into_cvs(tickers: list) -> bool:
#   # 1) Initialize an empty dataframe to store all the financial data:
#   final_df = pd.DataFrame()
#   # 2) Iterate through all ticker in tickers:
#   for ticker in tickers:
#     # 2.1) Gather the stock's financial data for past 5y:
#     stock = yf.Ticker(ticker)
#     stock_df = stock.history(start="2024-07-01", end="2024-08-06")
#     # 2.2) Assess if there df is empty => don't use this stock
#     if not stock_df.empty:
#       # 2.3) Add the stock's ticker symbol as a column:
#       stock_df['Ticker'] = ticker
#       # 2.4) append stock_df into the dataframe that will be converted into a CSV file:
#       final_df = pd.concat([final_df, stock_df])
#     else:
#        logger.info(f"No financial data could be gathered for the following stock {ticker}")

#   # 3) Assess whether the final dataframe is empty:
#   if final_df.empty:
#     logger.error(f"Error: The dataframe used to store all stock's financial result is empty")
#     return False
  
#   # 4) If final DF not empty, attempt to convert it in CVS
#   result = await convert_df_to_csv(final_df)
#   # 5) If operation was successful attempt to write the date where data ends_
#   if result:
#      return await write_date_when_retrieved()
#   return False









### Purpose: Add the latest financial data gathered at the end of the CVS file:
async def add_data_to_csv(new_df: pd.DataFrame) -> bool:
    try:
        # 1) Ensure the index is named 'Date' and is in datetime format:
        new_df.index.name = 'Date'
        new_df.index = pd.to_datetime(new_df.index, errors='coerce')

        # 2) Attemot to read the existing CSV file if it exists:
        if os.path.exists(CSV_FILE_PATH):
            async with aiofiles.open(CSV_FILE_PATH, mode='r') as file:
                content = await file.read()
            existing_df = pd.read_csv(io.StringIO(content), index_col='Date', parse_dates=True)
            # 2.1) Combine the existing DataFrame (data from csv file) with the new DataFrame with the latest data:
            combined_df = pd.concat([existing_df, new_df])
        else:
            combined_df = new_df

        # 3) Ensure 'Date' is the index and write to CSV
        combined_df.reset_index(inplace=True)
        combined_df.set_index('Date', inplace=True)
        
        # 4) Write the combined data to the CSV file
        async with aiofiles.open(CSV_FILE_PATH, mode='w') as file:
            await file.write(combined_df.to_csv())
        print("Financial data successfully updated in the CSV file.")
        
        # 5) Attempt to Sort the CSV file
        success = await sort_csv_file(CSV_FILE_PATH)
        return success
    except Exception as e:
        print(f"Failed to update data in CSV file: {e}")
        return False









### Purpose: Sort the CSV file so that stocks are grouped according to date and to their ticker:
async def sort_csv_file(file_path: str):
    try:
        # 1) Attempt to read the CSV file:
        async with aiofiles.open(file_path, mode='r') as file:
            content = await file.read()
        # 1.1) Store the content of the CSV into a DataFrame:
        df = pd.read_csv(io.StringIO(content), parse_dates=['Date'])
        # 1.2) Ensure the 'Date' column is in datetime format:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # 1.3) Drop rows with NaN values in 'Date' column:
        df.dropna(subset=['Date'], inplace=True)
        # 1.4) Sort the DataFrame by 'Ticker' and 'Date':
        df.sort_values(by=['Ticker', 'Date'], inplace=True)
        # 1.5) Remove duplicates, keeping the last occurrence:
        df.drop_duplicates(subset=['Ticker', 'Date'], keep='last', inplace=True)
        
        # 2) Attempt to write the sorted DataFrame back to the CSV file
        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(df.to_csv(index=False))
        
        print("CSV file successfully sorted.")
        return True
    except Exception as e:
        print(f"Failed to sort CSV file: {e}")
        return False







### Purpose: Gather missing financial data for all stocks from SP500:
async def get_missing_recent_data(tickers: list) -> bool:
    # 1) Initialize an empty DataFrame to store all the financial data:
    final_df = pd.DataFrame()
    # 2) Set the last closing day you want to get:
    yesterday_closing_date = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Yesterday's closing price is: {yesterday_closing_date}")
    print(f"Yesterday's closing price is: {yesterday_closing_date}")
    # 3) Attempt to retrieve the most recent date worth of financial data from txt file:
    # 3) This date represents the latest closing date of data we have in the csv file:
    last_closing_date_in_csv = await get_latest_date_of_financial_data()
    logger.info(f"The last closing date in CSV retrieved is: {last_closing_date_in_csv}")
    print((f"The last closing date in CSV retrieved is: {last_closing_date_in_csv}"))
    # 3.1) If operation was successful: Convert the date to strptime in the format YYYY-MM-DD:
    if last_closing_date_in_csv:
        last_closing_date_in_csv = (datetime.strptime(last_closing_date_in_csv, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"last closing date in CSV: {last_closing_date_in_csv}")
        # 4) Iterate through all tickers in the list:
        for ticker in tickers:
            # 4.1) Gather all financial data from last_closing_date to the most recent one = yesterday_closing_date:
            stock = yf.Ticker(ticker)
            stock_df = stock.history(start=last_closing_date_in_csv, end=yesterday_closing_date)
            # 4.2) Assess if the df of this stock is empty => don't use this stock:
            if not stock_df.empty:
                # 4.3) Add the stock's ticker symbol as a column:
                stock_df['Ticker'] = ticker
                # 4.4) Concat the stock_df with the final dataframe:
                final_df = pd.concat([final_df, stock_df])
            else:
                logger.info(f"No financial data could be gathered for the following stock {ticker}")
    
        # 5) Assess if the final dataframe where all stock's financial data is empty:
        if final_df.empty:
            logger.error("Error: The dataframe used to store all stock's financial results is empty")
            return False
        # 5.1) If dataframe not empty, try to append the latest data into the CSV file:
        else:
            success = await add_data_to_csv(final_df)
            # 5.2) If operation was successful, try to write the latest date worth of data retrieved into the txt file:
            if success:
                return await write_date_when_retrieved()
            else:
                return False
    else:
        logger.error("Error: Unable to get the latest date of financial data")
        return False