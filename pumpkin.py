import pandas as pd
import yfinance as yf
import numpy as np



start_year = int(input("Enter start year:"))
end_year = int(input("Enter end year:"))

data_start = start_year - 1

airlines = ["DAL", "UAL", "AAL", "LUV", "ALK", "RYAAY"]
banks = ["PNC", "USB", "TFC", "FITB", "CFG", "MTB"]
oil_gas = ["COP", "EOG", "OXY", "FANG", "DVN", "CTRA"]
homebuilders = ["DHI", "LEN", "PHM", "NVR", "TMHC", "KBH"]

# airline



    # Strategy: finds best and worst performing stocks from industry over a certain window
    # action: short the best, long the worst

    # goal: for each window value, it will produce the trading strategy
    # return: out of the windows -> the best will be singled out (the window "value" will be given)

    # brings in data and sets it up

    # creates the dataframe for function results (for each "window" value tested)


data_airlines = yf.download(airlines, start=f"{data_start}-01-01",auto_adjust=True)
data_raw = data_airlines['Close'].copy()
    
for t in airlines:
    data_airlines = data_raw.copy()

    data_airlines[f'{t}_Return_Window'] = data_airlines[t].pct_change(30)
    data_airlines[f'{t}_Daily_Return'] = data_airlines[t].pct_change(1)

data = data_airlines.loc[f"{start_year}-01-01":].copy()



print(data.head())
