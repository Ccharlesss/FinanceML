# SP500 = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'META', 'GOOGL', 'GOOG', 'LLY', 'JPM', 'AVGO', 'XOM', 'UNH', 
#         'V', 'TSLA', 'PG', 'MA', 'JNJ', 'HD', 'MRK', 'COST', 'ABBV', 'CVX', 'CRM', 'BAC', 'WMT', 'NFLX', 'PEP', 
#         'AMD', 'KO', 'WFC', 'LIN', 'TMO', 'ADBE', 'DIS', 'ACN', 'MCD', 'CSCO', 'ABT', 'ORCL', 'CAT', 'QCOM', 'INTU', 
#         'GE', 'IBM', 'VZ', 'CMCSA', 'DHR', 'AMAT', 'COP', 'TXN', 'PM', 'NOW', 'PFE', 'AMGN', 'INTC', 'UNP', 
#         'UBER', 'LOW', 'GS', 'NEE', 'RTX', 'AXP', 'SPGI', 'ISRG', 'HON', 'PGR', 'ELV', 'MU', 'BKNG', 'ETN', 'C', 'T', 
#         'MS', 'LRCX', 'NKE', 'SCHW', 'TJX', 'SYK', 'DE', 'MDT', 'UPS', 'BLK', 'VRTX', 'CB', 'LMT', 'BMY', 'CI', 'SBUX', 
#         'ADP', 'BSX', 'MMC', 'PLD', 'BA', 'REGN', 'ADI', 'MDLZ', 'CVS', 'FI', 'BX', 'PANW', 'KLAC', 'GILD', 'TMUS', 'SNPS', 
#         'AMT', 'CMG', 'SO', 'DUK', 'CME', 'TGT', 'ICE', 'MO', 'EOG', 'WM', 'CDNS', 'FCX', 'SLB', 'SHW', 'CL', 'MPC', 'EQIX', 
#         'TT', 'ABNB', 'NOC', 'CSX', 'GD', 'MCK', 'TDG', 'PYPL', 'ITW', 'PSX', 'ZTS', 'APH', 'PH', 'BDX', 'EMR', 'FDX', 
#         'HCA', 'ORLY', 'PNC', 'AON', 'ANET', 'USB', 'CTAS', 'ROP', 'PCAR', 'MAR', 'MCO', 'MSI', 'CEG', 'ECL', 'NXPI', 
#         'VLO', 'NSC', 'COF', 'WELL', 'DXCM', 'APD', 'AJG', 'TRV', 'MMM', 'TFC', 'AZO', 'HLT', 'EW', 'GM', 'AIG', 'F', 
#         'ALL', 'AEP', 'CPRT', 'ROST', 'NUE', 'ADSK', 'SPG', 'OKE', 'WMB', 'CARR', 'TEL', 'MCHP', 'SRE', 'AFL', 'O', 
#         'KMB', 'DHI', 'PSA', 'CCI', 'NEM', 'FTNT', 'BK', 'GWW', 'CNC', 'MSCI', 'LULU', 'MET', 'D', 'HES', 'GIS', 'OXY',
#         'DLR', 'FIS', 'STZ', 'PRU', 'AMP', 'AME', 'JCI', 'URI', 'IQV', 'COR', 'IR', 'PCG', 'DOW', 'CMI', 'PAYX', 
#         'LEN', 'FAST', 'A', 'FANG', 'LHX', 'IDXX', 'CTVA', 'MNST', 'EXC', 'RSG', 'SMCI', 'HUM', 'KR', 'OTIS', 'SYY', 
#         'ODFL', 'MLM', 'YUM', 'KMI', 'KDP', 'CSGP', 'DVN', 'HAL', 'EL', 'GPN', 'PEG', 'ACGL', 'VRSK', 'VMC', 'ADM',
#         'BKR', 'CTSH', 'DFS', 'CDW', 'PWR', 'IT', 'DD', 'MRNA', 'ED', 'DG', 'ANSS', 'DAL', 'BIIB',
#         'PPG', 'FICO', 'XEL', 'HSY', 'FTV', 'HIG', 'KHC', 'ROK', 'XYL', 'WST', 'EA', 'MPWR', 'EXR', 'RCL', 'VICI',
#         'VST', 'TSCO', 'NVR', 'TRGP', 'CHTR', 'PHM', 'RJF', 'ON', 'KEYS', 'CAH', 'LYB', 'RMD', 'GLW', 'AVB', 'HWM', 
#         'ZBH', 'FITB', 'WTW', 'DLTR', 'HPQ', 'EIX', 'MTD', 'EFX', 'WEC', 'CBRE', 'CHD', 'DOV', 'TROW', 'EBAY', 
#         'NDAQ', 'MTB', 'WAB', 'FE', 'PTC', 'AWK', 'ALGN', 'WY', 'HPE', 'GRMN', 'CBOE', 'HBAN', 'ULTA', 'AEE', 'BRO', 
#         'NTAP', 'STT', 'HUBB', 'IRM', 'STLD', 'TDY', 'ES', 'BR', 'TTWO', 'APTV', 'IFF', 'CINF', 'EQR', 'ETR', 
#         'PPL', 'AXON', 'GPC', 'STE', 'BAX', 'BALL', 'DECK', 'WDC', 'DTE', 'INVH', 'MOH', 'CPAY', 'CTRA', 'SBAC',
#         'BLDR', 'WBD', 'LUV', 'TSN', 'HOLX', 'LH', 'CLX', 'FSLR', 'CF', 'CMS', 'OMC', 'CAG', 'SWKS', 'PFG', 'DPZ', 
#         'EXPE', 'RF', 'ATO', 'CNP', 'PKG', 'BG', 'TER', 'TXT', 'DRI', 'EG', 'MAS', 'ILMN', 'EQT', 'J', 'K', 'MAA', 
#         'AVY', 'IEX', 'STX', 'LDOS', 'JBL', 'VRSN', 'ARE', 'MKC', 'EXPD', 'AKAM', 'UAL', 'WRB', 'MRO', 'CE', 'TYL', 
#         'NRG', 'FDS', 'COO', 'VTR', 'ENPH', 'LVS', 'SYF', 'CFG', 'WAT', 'NTRS', 'ESS', 'POOL', 'EVRG', 'JBHT', 'PNR', 
#         'ALB', 'SNA', 'ZBRA', 'SJM', 'EMN', 'IP', 'HST', 'HII', 'CCL', 'AMCR', 'FFIV', 'LKQ', 'GEN', 'UDR', 'DGX', 
#         'LNT', 'JKHY', 'SWK', 'AES', 'VTRS', 'MGM', 'KEY', 'LYV', 'NDSN', 'PODD', 'TAP', 'EPAM', 'IPG', 'RVTY', 'KMX', 
#         'ALLE', 'NI', 'WBA', 'DOC', 'TRMB', 'L', 'KIM', 'AOS', 'CRL', 'LW', 'BBY', 'ROL', 'JNPR', 'FMC', 'REG', 'PNW', 
#         'AAL', 'HRL', 'RHI', 'APA', 'BBWI', 'FRT', 'CHRW', 'DVA', 'CTLT', 'IVZ', 'HAS', 'BWA', 'BEN', 'MTCH', 'CZR', 'WYNN',
#         'DAY', 'NWSA', 'CPB', 'INCY', 'TPR', 'FOXA', 'TFX', 'QRVO', 'BXP', 'CPT', 'AIZ', 'ETSY', 
#         'CMA', 'RL', 'HSIC', 'MKTX', 'PAYC', 'MOS', 'TECH', 'NCLH', 'GNRC', 'UHS', 'NWS', 'PARA', 'FOX', 'GL', 'MHK', 'BIO']


# Stocks removed bcs no data or insufficient data = ['other','GEV','KVUE','GEHC','VLTO','SOLV', 'BN.F', 'BRK.B', 'BF.B', 'WRK']
# ===========================================================================================================================


SP500 = ['MSFT', 'AAPL', 'NVDA']


# CSV_FILE_PATH = "src/StockData/historical_data.csv"
CSV_FILE_PATH = "src/StockData/blabla-data.csv" # For testing

# DATE_FILE_PATH = "src/StockData/date_when_updated.txt"
DATE_FILE_PATH = "src/StockData/date_when_updated_test.txt" # For testing