from venv import logger
import yfinance as yf
import pandas as pd
import numpy as np

from sklearn import metrics
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score, classification_report


# Import the library used to compute all the necessary financial indicators:
from ta.momentum import StochasticOscillator
from ta.momentum import ROCIndicator
from ta.trend import MACD
from ta.volume import OnBalanceVolumeIndicator

# Import the File where all training data is located:
from src.Context.StockContext import CSV_FILE_PATH, SP500





### ========================================================================================================
###                                           Retrieve data From CSV to DF
async def retrieve_data_from_cvs_to_df(ticker: str) -> pd.DataFrame:
    try:
        # 1) Load the CSV file into a DataFrame
        df = pd.read_csv(CSV_FILE_PATH, parse_dates=['Date'])
        # 2) Filter the DataFrame by the specified ticker
        ticker_df = df[df['Ticker'] == ticker]
        # 3) Select the desired columns
        selected_columns = ['Date', 'High', 'Low', 'Close', 'Volume']
        ticker_df = ticker_df[selected_columns]
        # 4) Set the Date column as the index
        ticker_df.set_index('Date', inplace=True)
        return ticker_df
  
    except Exception as e:
        print(f"Failed to retrieve data for ticker {ticker}: {e}")
        return None
### ========================================================================================================
    





### ========================================================================================================
###                  COMPUTE RSA / K% / D% / R% / PROC / MACD / MACD_Signal / MACD_Diff / OBV

### Purpose: Compute RSI:
async def compute_rsi(data: pd.DataFrame) -> pd.DataFrame:
    # 1) verif if the DataFrame is empty:
    if data.empty:
        logger.error(f"The data frame for the computation of the RSI is empty. Cant compute RSI")
        return None
    
   # 2.1) Compute ΔP (DeltaP):
    data["Delta-P"] = data["Close"].diff()
    # 2.2) Set the nbr of days:
    nbr_days = 14
    # 2.3) Create 2 parallel DF:
    up_df = data["Delta-P"].copy()
    down_df = data["Delta-P"].copy()
    # 2.4) For up days if ΔP<0 => up_df=0. for Down days, if ΔP>0 => down_df=0:
    up_df[up_df<0] = 0
    down_df[down_df>0] = 0
    # 2.5) Ensure ΔP<0 has only absolute values:
    down_df = down_df.abs()
    # 2.6) compute the Exponential Weighted Moving Average (EWMA): Give more weight to more recent prices:
    ewma_up = up_df.transform(lambda x: x.ewm(span=nbr_days).mean())
    ewma_down = down_df.transform(lambda x: x.ewm(span=nbr_days).mean())
    # 2.7) Compute the Relative Strength Index (RSI):
    relative_strength = ewma_up / ewma_down
    rsi = 100.0 - (100.0 / (1.0 + relative_strength))
    # 2.8) Clean the data to return Original DataFrame with RSI:
    data["RSI"] = rsi
    data = data.drop('Delta-P', axis=1)
    # 2.9) Assess whether the RSI column isnt empty:
    if data["RSI"].isnull().all():
        logger.error("The OBV column is empty or contains only Nan values.")
        return None
    return data


### Purpose: Compute the Srochastic oscillator = {K%, D%, R%}:
async def compute_stochastic_oscillators(data: pd.DataFrame, window=14, smooth_window=3) -> pd.DataFrame:
     # 1) Initialize the stochastic Oscillator:
    stoch = StochasticOscillator(high=data['High'],low=data['Low'],close=data['Close'],window=window,smooth_window=smooth_window)
    # 2) Compute the K%:
    data["K%"]=stoch.stoch()
    # 3) Compute the D% (Moving avr of K%):
    data["D%"]=stoch.stoch_signal()
    # 4) Compute the R%:
    data["R%"]=-100 * (data['High'].rolling(window=window).max() - data['Close']) / (data['High'].rolling(window=window).max() - data['Low'].rolling(window=window).min())
    # 5) Assess whether the Column K%, D% and R% isn't empty:
    if data[["K%", "D%", "R%"]].isnull().all().any():
      logger.error("One or more of the columns K%, D%, and R% are empty or contain only NaN values.")
      return None
    return data


### Purpose: Compute the PROC:
async def compute_proc(data: pd.DataFrame, window=14) -> pd.DataFrame:
    # 1) Initialize ROCIndicator:
    roc = ROCIndicator(close=data["Close"],window=window)
    # 2) Compute PROC:
    data["PROC"] = roc.roc()
    # 3) Assess whether the PROC column isn't empty:
    if data["PROC"].isnull().all():
        logger.error("The PROC column is either empty or only contains Nan values.")
        return None
    return data

### Purpose: Compute the MACD:
async def compute_macd(data: pd.DataFrame, window_slow=26, window_fast=12, window_sign=9) -> pd.DataFrame:
    # 1) Initialize MACD indicator:
    macd = MACD(close=data["Close"], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
    # 2) Compute MACD:
    data['MACD'] = macd.macd()
    # 3) Compute MACD Signal:
    data['MACD_Signal'] = macd.macd_signal()
    # 4) Compute MACD Diff (# This is the MACD Histogram)
    data['MACD_Diff'] = macd.macd_diff()
    # 5) Assess whether one or all of the columns arent empty:
    if data[['MACD', 'MACD_Signal','MACD_Diff']].isnull().all().any():
        logger.error("One or all of the Computed column (MACD, MACD_Signal, MACD_Diff) is either empty oor only contains Nan values.")
        return None
    return data


### Purpose: Compute the On Balance Value:
async def compute_obv(data: pd.DataFrame) -> pd.DataFrame:
    # 1) Initialive the OBVIndicator:
    obv = OnBalanceVolumeIndicator(close=data["Close"], volume=data["Volume"])
    # 2) Compute the OBV:
    data["OBV"] = obv.on_balance_volume()
    # 3) Assess whether the OBV column is empty:
    if data["OBV"].isnull().all():
        logger.error("The OBV column is either empty or only contains Nan values.")
        return None
    return data



### Purpose: Compute Financial Features X and remove Nan values:
async def compute_features_and_remove_nan(df: pd.DataFrame) -> pd.DataFrame:
    # 1) Compute all financial indicators
    df = await compute_rsi(df)
    if df is None:
        logger.error("An error occured in the computation of RSI.")
        return None

    df = await compute_stochastic_oscillators(df)  # await is required here
    if df is None:
        logger.error("An error occured in the computation of K%, D%, or R%.")
        return None

    df = await compute_proc(df)  # await is required here
    if df is None:
        logger.error("An error occured in the computation of PROC.")
        return None

    df = await compute_macd(df)  # await is required here
    if df is None:
        logger.error("An error occured in the computation of MACD, MACD_Signal or MACD_Diff.")
        return None

    df = await compute_obv(df)  # await is required here
    if df is None:
        logger.error("An error occured in the computation of OBV.")
        return None

    # 2) Remove Nan values:
    df = df.dropna()
    return df

 ### ========================================================================================================   








### ========================================================================================================
###                            Generate the Prediction Column / Remove Unnecessary features
async def generate_prediction_column(df: pd.DataFrame) -> pd.DataFrame:
    # 1) Market trend if close_f < close_i => 0 (down). else => 1 (up):
    closed_groups = df["Close"].transform(lambda x: x.shift(1) < x)
    # 1.1) Convert boolean values to int {0/1}:
    closed_groups = closed_groups * 1
    # 1.2) Create a new  column called prediction=y (label):
    df["Prediction"] = closed_groups
    # 1.3) Remove unwanted features:
    df = df.drop(['High', 'Low', 'Close', 'Volume'], axis=1)
    # 2) Assess whether the prediction column contains values 1/0:
    if not df["Prediction"].isin([0,1]).all():
        logger.error("The Prediction column contfshdshfdains values other than 0 or 1.")
        return None
    return df
 ### ========================================================================================================   






### ========================================================================================================
###                            Perform the computation for tommorow's closing price trend
async def compute_random_forest(df: pd.DataFrame):
    # 1) Divide the dataset into features=x and labels=y:
    x_column = df[["RSI", "K%", "R%", "D%", "PROC", "MACD", "MACD_Signal", "MACD_Diff", "OBV"]]
    y_column = df["Prediction"]

    # 2) Perform Time Series Cross Validation:
    # 2.1) Define the nbr of splits
    tscv = TimeSeriesSplit(n_splits=10)
    mae_scores = [] # Used to store the mean absolute error for each fold:
    split_ratios = [] # Used to store the training set ration for each fold:
    # 2.2) Iterates through each fold K created by tscv.split():
    for fold_idx, (train_index, test_index) in enumerate(tscv.split(x_column)):
        # 2.3) Create a training and a test set:
        x_train, x_test = x_column.iloc[train_index], x_column.iloc[test_index]
        y_train, y_test = y_column.iloc[train_index], y_column.iloc[test_index]
        # 2.4) Train the Random Forest model on the training data:
        forest = RandomForestClassifier(n_estimators=100, max_depth=10, max_features='sqrt', random_state=42, criterion='gini', oob_score=True)
        forest.fit(x_train, y_train)
        # 2.5) Compute the ratio of the training set size to the total data size:
        train_ratio = len(train_index) / (len(train_index) + len(test_index))
        # 2.6) Append the computed train ratio to the split ratio:
        split_ratios.append(train_ratio)
        # 2.7) Predictions made by the model on the test set:
        y_pred = forest.predict(x_test)
        # 2.8) Compute the mean absolute error btw y-test and y-pred:
        mae = mean_absolute_error(y_test, y_pred)
        # 2.9) Append the MAE to the MAE list:
        mae_scores.append(mae)
        # 2.10) Print the result for the current fold:
        print(f'Fold {fold_idx + 1} - MAE: {mae:.4f}, Train Ratio: {train_ratio:.2f}')

    # 3) Compute the Avr MAE accross fold and determine best fold: (split btw training and test data):
    average_mae = sum(mae_scores) / len(mae_scores)
    print(f'Average MAE: {average_mae:.4f}')
    # 4) Find the best fold with the Lowest MAE:
    best_fold_idx = mae_scores.index(min(mae_scores))
    best_train_ratio = split_ratios[best_fold_idx]
    print(f'Best Fold: {best_fold_idx + 1}, MAE: {mae_scores[best_fold_idx]:.4f}, Best Train Ratio: {best_train_ratio:.2f}')
    # 5) Create the final training and testing set based on the best training ratio:
    train_size = int(best_train_ratio * len(x_column))
    x_train_final, x_test_final = x_column[:train_size], x_column[train_size:]
    y_train_final, y_test_final = y_column[:train_size], y_column[train_size:]

    # 6) Define the parameter grid for GridSearchCV:
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'max_features': ['sqrt', 'log2'],
        'criterion': ['gini', 'entropy']
    }

    # 7) Initialize the Random Forest classifier:
    forest = RandomForestClassifier(random_state=42, oob_score=True)
    # 8) Perform Grid Search with cross-validation:
    grid_search = GridSearchCV(estimator=forest, param_grid=param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(x_train_final, y_train_final)
    # 9) Get the best estimator:
    best_forest = grid_search.best_estimator_
    print(f'Best Parameters: {grid_search.best_params_}')

    # 10) Evaluate the final model on the test set:
    # 10.1) Predictions made by the best model on the final test set:
    y_pred_final = best_forest.predict(x_test_final)
    # 10.2) Compute MAE btw y-test-final, y-pred-final:
    final_mae = mean_absolute_error(y_test_final, y_pred_final)
    print(f'Final MAE on best split: {final_mae:.4f}')
    # 10.3) Print the OOB Score if available:
    if hasattr(best_forest, 'oob_score_'):
        print(f'OOB Score: {best_forest.oob_score_:.4f}')
    # 10.4) Compute and print the accuracy:
    accuracy = accuracy_score(y_test_final, y_pred_final)
    print("Correct prediction (%):", accuracy * 100)

    # 11) Predict the trend for tomorrow based on the latest available data:
    # 11.1) Selects the latest available data (last row of x_column):
    latest_data = x_column.iloc[-1:]
    # 11.2) Makes a prediction for the next day's trend using the best model:
    next_day_prediction = best_forest.predict(latest_data)
    print(f'Tomorrow\'s closing price trend prediction: {"Higher" if int(next_day_prediction[0]) == 1 else "Lower"}')
    # 11.3) Return the predicted label:
    return int(next_day_prediction[0])
### ========================================================================================================



### ========================================================================================================
###                                # Function called by the Random Forest Route
async def orchestrate_random_forest(ticker: str) -> int:
  # 1) Retrieve appropriate financial data from the CSV file:
  dataset = await retrieve_data_from_cvs_to_df(ticker)
  if dataset is None or dataset.empty:
      logger.error(f"Error, the dataFrame Doesn't contain any data")
      return None
  # 2) Compute all the required financial indicators to make the prediction:
  dataset = await compute_features_and_remove_nan(dataset)
  if dataset is None or dataset.empty:
      logger.error("An error occured in the computation of financial featues.")
      return None
  # 3) Generate the Preduction column and remove unecessary features {High, Low, Close, Volume}:
  dataset = await generate_prediction_column(dataset)
  if dataset is None or dataset.empty:
      logger.error("An error in the generation of the prediction column.")
      return None
  # 4) Predict tomorrow's closing price trend:
  return await compute_random_forest(dataset)
