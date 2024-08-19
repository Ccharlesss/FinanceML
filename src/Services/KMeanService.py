from venv import logger
import pandas as pd
import numpy as np
import json



from pylab import plot,show
from matplotlib import pyplot as plt, ticker
import plotly.express as px
from plotly.graph_objs import Figure

from numpy.random import rand
from scipy.cluster.vq import kmeans,vq
from math import sqrt
from sklearn.cluster import KMeans 

# Import the tickers from the stock context:
from src.Context.StockContext import CSV_FILE_PATH








### ========================================================================================================
###                                    Retrieve data From CSV to DF on all tickers:
async def retrieve_data_to_df() -> pd.DataFrame:
    try:
        # 1) Load the CSV file into a DataFrame
        df = pd.read_csv(CSV_FILE_PATH, parse_dates=['Date'])
        # 2) Select the desired columns
        selected_columns = ['Date', 'Ticker','Close']
        df = df[selected_columns]
        # 3) Set the Date column as the index
        df.set_index('Date', inplace=True)
        return df
    
    except Exception as e:
        print(f"Failed to retrieve data from {CSV_FILE_PATH}: {e}")
        return pd.DataFrame()





### ========================================================================================================
###                      Compute Financial Features X = {Avr annual return, Avr annual volatility}: 

### Purpose: Compute Avr annual return and volatility of all stocks and return it in a DF:
async def compute_avg_annual_return_and_volatility(df: pd.DataFrame) -> pd.DataFrame:
  # 1) Generate a DF with The Date as index and Close and Ticker as column:
  pivot_df = df.pivot(columns='Ticker', values='Close')
  # 2) Handle missing values explicitly using ffill and bfill:
  pivot_df.ffill(inplace=True)
  pivot_df.bfill(inplace=True)
  # 3) Compute daily returns:
  daily_returns = pivot_df.pct_change(fill_method=None)
  # 4) Calculate the average annual return:
  avg_annual_return = daily_returns.mean() * 252
  # 5) Compute annual volatility (std of daily returns scaled by sqrt root of 252 = nbr of traiding days/years):
  annual_volatility = daily_returns.std() * np.sqrt(252)
  # 6) Combine the result into a single Dataframe:
  result_df = pd.DataFrame({'Avr Annual Return': avg_annual_return, 'Avr Annual Volatility': annual_volatility})
  # 7) Ensure there is no Nan values or that one or more column is empty:
  if result_df[['Avr Annual Return', 'Avr Annual Volatility']].isnull().all().any():
    logger.error("Error, either the Avr Annual Return or the Avr Annual Volatility or both are either empty or contains Nan values.")
    return None
  return result_df



### ========================================================================================================
###                                        Remove outliers in Kmeans:

### Purpose: Remove potential outliers that would induce biais in the kmean algorithm:
async def remove_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
  # 1) Compute Q1 (25th percentile) and Q3 (75th percentile):
  Q1 = df[['Avr Annual Return', 'Avr Annual Volatility']].quantile(0.25)
  Q3 = df[['Avr Annual Return', 'Avr Annual Volatility']].quantile(0.75)
  # 2) Calculate the IQR:
  IQR = Q3 - Q1
  # 3) Define the lower and upper bounds for outliers:
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR
  # 4) Filter out the outliers:
  df_no_outliers = df[~((df[['Avr Annual Return', 'Avr Annual Volatility']] < lower_bound) |
                        (df[['Avr Annual Return', 'Avr Annual Volatility']] > upper_bound)).any(axis=1)]
  # 5) Identify and print outliers:
  outliers = df[((df[['Avr Annual Return', 'Avr Annual Volatility']] < lower_bound) |
                  (df[['Avr Annual Return', 'Avr Annual Volatility']] > upper_bound)).any(axis=1)]
      
  if not outliers.empty:
    print("Identified outliers:")
    print(outliers)
    
  return df_no_outliers
  

  
### ========================================================================================================
###                                        Perform the Kmeans model:
async def perform_kmeans_and_create_dataframe(df: pd.DataFrame, n_clusters: int = 4, random_state: int = 42) -> str:
    # 1) Ensure the DataFrame has the required columns:
    if 'Avr Annual Return' not in df.columns or 'Avr Annual Volatility' not in df.columns:
        logger.error("Error: DataFrame does not contain the required columns for computation.")
        return None
    
    try:
        # 2.1) Extract the relevant data from the DataFrame:
        dataset = df[['Avr Annual Return', 'Avr Annual Volatility']].values
        # 2.2) Initialize the K-Means algorithm:
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
        # 2.3) Fit the K-Means algorithm to the dataset:
        kmeans.fit(dataset)
        # 2.4) Extract the x and y coordinates from the dataset:
        x = dataset[:, 0]  # Avr Annual Return
        y = dataset[:, 1]  # Avr Annual Volatility
        
        # 2.5) Create a DataFrame for the clustered data:
        result_df = pd.DataFrame({
            'Ticker': df.index,  # Assuming the DataFrame index contains the tickers
            'Avr Annual Return': x,
            'Avr Annual Volatility': y,
            'Cluster': kmeans.labels_
        })
        
        # 3) Convert the DataFrame to a JSON object:
        result_json = result_df.to_json(orient='index')
        
        return result_json

    except Exception as e:
        logger.error(f"An error occurred while performing K-Means clustering: {e}")
        return None  # Return None if any error occurs




### ========================================================================================================
###                                      Orchestrate Kmean computation:
### Purpose: Generate the Kmean and return an interactive graph:
async def orchestrate_kmean_and_plot():
  # 1) Attempt to retrieve Data from CSV file and convert it to pd.DataFrame:
  initial_df = await retrieve_data_to_df()
  if initial_df is None or initial_df.empty:
    logger.error("An error occured in the retrieval and conversion of data from CSV to pd.DataFrame.")
    return None
  
  # 2) Attempt to compute the the Avr Annual Return and Volatility of all stocks:
  # 2) returned dataframe format: ticker symbol as index, Avr Annual Return and Avr Annual Volatility as column:
  initial_df = await compute_avg_annual_return_and_volatility(initial_df)
  if initial_df is None or initial_df.empty:
    logger.error("An error occured in the computation of the Annual Avr Return and Volatility.")
    return None
  
  # 3) Remove outliers:
  initial_df = await remove_outliers_iqr(initial_df)
  if initial_df is None or initial_df.empty:
    logger.error("An error occured in the operation to remove outliers.")
    return None
  
  # 4) Perform the KMean algorithm and return an interactive plot:
  # result = await perform_kmeans_and_plot(initial_df)
  result = await perform_kmeans_and_create_dataframe(initial_df)
  if result is None:
    logger.error("An error occured in the computation of Kmean and the generation of the plot.")
  return result