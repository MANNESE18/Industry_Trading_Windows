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

def airlines_strategy_1(window):

    # Strategy: finds best and worst performing stocks from industry over a certain window
    # action: short the best, long the worst

    # goal: for each window value, it will produce the trading strategy
    # return: out of the windows -> the best will be singled out (the window "value" will be given)

    # brings in data and sets it up

    # creates the dataframe for function results (for each "window" value tested)


    data_airlines = yf.download(airlines, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_airlines['Close'].copy()

    Strat_1_Airlines = pd.DataFrame(index=windows_to_test)
    Rankings_1_Airlines = pd.DataFrame(index=windows_to_test)
    
    for w in windows_to_test:
        
        data_airlines = data_raw.copy()

        for t in airlines:
            data_airlines[f'{t}_Return_Window'] = data_airlines[t].pct_change(w)
            data_airlines[f'{t}_Daily_Return'] = data_airlines[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in airlines]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_airlines = data_airlines.dropna(subset=return_columns, how='all')

        # filters for ticker w/ highest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_airlines['Ticker_Highest'] = data_airlines[return_columns].idxmax(axis=1)
        data_airlines['just_the_ticker_H'] = data_airlines['Ticker_Highest'].str.replace('_Return_Window', '')                                                           
        data_airlines['Trade_Highest'] = data_airlines['just_the_ticker_H'].shift(1)
        data_airlines['Ticker_Highest_Daily'] = data_airlines.apply(lambda x: x[f"{x['Trade_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Highest']) else 0, axis=1)

        # filters for ticker w/ lowest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_airlines['Ticker_Lowest'] = data_airlines[return_columns].idxmin(axis=1)
        data_airlines['just_the_ticker_L'] = data_airlines['Ticker_Lowest'].str.replace('_Return_Window', '')                                                           
        data_airlines['Trade_Lowest'] = data_airlines['just_the_ticker_L'].shift(1)                                                               
        data_airlines['Ticker_Lowest_Daily'] = data_airlines.apply(lambda x: x[f"{x['Trade_Lowest']}_Daily_Return"]if pd.notnull(x['Trade_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_airlines['Short_Long_Strategy'] = data_airlines['Ticker_Highest_Daily']*(-1) + data_airlines['Ticker_Lowest_Daily']

        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_airlines.loc[f"{start_year}-01-01":].copy()

        
        data_filtered['Strategy_1_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1                                                                    
        Total_Return = data_filtered['Strategy_1_Return'].iloc[-1]                                                         
    
        # find sharpe ratio
        airlines_1_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        airlines_1_daily_mean = airlines_1_daily.mean()
        airlines_1_daily_std = airlines_1_daily.std()
        if airlines_1_daily_std != 0:
            sharpe = (airlines_1_daily_mean/airlines_1_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_1_Airlines.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_1_Airlines.loc[w, 'Return'] = Total_Return
        Strat_1_Airlines.loc[w, 'Max_Drawdown'] = Max_Drawdown

        # takes column for each data measure -> ranks them from ideal to non ideal
        # takes rank and multiplies it by -> adds up 3 values for each window and ranks Ranking_Score from low to high
        # returns the window w/ the best performance (lowest overall Ranking_Score = top of list)
    Rankings_1_Airlines['Sharpe_Rank'] = Strat_1_Airlines['Sharpe'].rank(ascending=False)
    Rankings_1_Airlines['Return_Rank'] = Strat_1_Airlines['Return'].rank(ascending=False)
    Rankings_1_Airlines['Drawdown_Rank'] = Strat_1_Airlines['Max_Drawdown'].rank()
    Rankings_1_Airlines['Final_Score'] = (
        (Rankings_1_Airlines['Sharpe_Rank'])*(.4) +
        (Rankings_1_Airlines['Return_Rank'])*(.4) +
        (Rankings_1_Airlines['Drawdown_Rank'])*(.2)
        )
    Best_Window_1_Airlines = Rankings_1_Airlines['Final_Score'].idxmin()

    return Strat_1_Airlines, Best_Window_1_Airlines

# put final window and its stats into new matrix / dataframe
    
def airlines_strategy_2(window):

    data_airlines = yf.download(airlines, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_airlines['Close'].copy()
    
    Strat_2_Airlines = pd.DataFrame(index=windows_to_test)
    Rankings_2_Airlines = pd.DataFrame(index=windows_to_test)

    for w in windows_to_test:

        data_airlines = data_raw.copy()

        for t in airlines:
            data_airlines[f'{t}_Return_Window'] = data_airlines[t].pct_change(w)
            data_airlines[f'{t}_Daily_Return'] = data_airlines[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in airlines]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_airlines = data_airlines.dropna(subset=return_columns, how='all')
        
        # second highest
        data_airlines['Second_Highest_Ticker'] = data_airlines[return_columns].mask(data_airlines[return_columns].apply(lambda x: x == x.max(), axis=1)).idxmax(axis=1)
        data_airlines['just_the_ticker_2L'] = data_airlines['Second_Highest_Ticker'].str.replace('_Return_Window', '')                 
        data_airlines['Trade_Second_Highest'] = data_airlines['just_the_ticker_2L'].shift(1)                                                             
        data_airlines['Ticker_Second_Highest_Daily'] = data_airlines.apply(lambda x: x[f"{x['Trade_Second_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Highest']) else 0, axis=1)

        # second lowest
        data_airlines['Second_Lowest_Ticker'] = data_airlines[return_columns].mask(data_airlines[return_columns].apply(lambda x: x == x.min(), axis=1)).idxmin(axis=1)
        data_airlines['just_the_ticker_2L'] = data_airlines['Second_Lowest_Ticker'].str.replace('_Return_Window', '')                 
        data_airlines['Trade_Second_Lowest'] = data_airlines['just_the_ticker_2L'].shift(1)                                                             
        data_airlines['Ticker_Second_Lowest_Daily'] = data_airlines.apply(lambda x: x[f"{x['Trade_Second_Lowest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_airlines['Short_Long_Strategy'] = data_airlines['Ticker_Second_Highest_Daily']*(-1) + data_airlines['Ticker_Second_Lowest_Daily']
        
        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_airlines[data_airlines.index.year >= start_year].copy()
        
        data_filtered['Strategy_2_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1
        Total_Return = data_filtered['Strategy_2_Return'].iloc[-1]                                                         

        # find sharpe ratio
        airlines_2_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        airlines_2_daily_mean = airlines_2_daily.mean()
        airlines_2_daily_std = airlines_2_daily.std()
        if airlines_2_daily_std != 0:
            sharpe = (airlines_2_daily_mean/airlines_2_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_2_Airlines.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_2_Airlines.loc[w, 'Return'] = Total_Return
        Strat_2_Airlines.loc[w, 'Max_Drawdown'] = Max_Drawdown


    Rankings_2_Airlines['Sharpe_Rank'] = Strat_2_Airlines['Sharpe'].rank(ascending=False)
    Rankings_2_Airlines['Return_Rank'] = Strat_2_Airlines['Return'].rank(ascending=False)
    Rankings_2_Airlines['Drawdown_Rank'] = Strat_2_Airlines['Max_Drawdown'].rank()
    Rankings_2_Airlines['Final_Score'] = (
        (Rankings_2_Airlines['Sharpe_Rank'])*(.4) +
        (Rankings_2_Airlines['Return_Rank'])*(.4) +
        (Rankings_2_Airlines['Drawdown_Rank'])*(.2)
        )
    Best_Window_2_Airlines = Rankings_2_Airlines['Final_Score'].idxmin()

    return Strat_2_Airlines, Best_Window_2_Airlines


# 3 other industries


def banks_strategy_1(window):

    data_banks = yf.download(banks, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_banks['Close'].copy()

    Strat_1_Banks = pd.DataFrame(index=windows_to_test)
    Rankings_1_Banks = pd.DataFrame(index=windows_to_test)
    
    for w in windows_to_test:
        
        data_banks = data_raw.copy()

        for t in banks:
            data_banks[f'{t}_Return_Window'] = data_banks[t].pct_change(w)
            data_banks[f'{t}_Daily_Return'] = data_banks[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in banks]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_banks = data_banks.dropna(subset=return_columns, how='all')

        # filters for ticker w/ highest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_banks['Ticker_Highest'] = data_banks[return_columns].idxmax(axis=1)
        data_banks['just_the_ticker_H'] = data_banks['Ticker_Highest'].str.replace('_Return_Window', '')                                                           
        data_banks['Trade_Highest'] = data_banks['just_the_ticker_H'].shift(1)
        data_banks['Ticker_Highest_Daily'] = data_banks.apply(lambda x: x[f"{x['Trade_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Highest']) else 0, axis=1)

        # filters for ticker w/ lowest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_banks['Ticker_Lowest'] = data_banks[return_columns].idxmin(axis=1)
        data_banks['just_the_ticker_L'] = data_banks['Ticker_Lowest'].str.replace('_Return_Window', '')                                                           
        data_banks['Trade_Lowest'] = data_banks['just_the_ticker_L'].shift(1)                                                               
        data_banks['Ticker_Lowest_Daily'] = data_banks.apply(lambda x: x[f"{x['Trade_Lowest']}_Daily_Return"]if pd.notnull(x['Trade_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_banks['Short_Long_Strategy'] = data_banks['Ticker_Highest_Daily']*(-1) + data_banks['Ticker_Lowest_Daily']

        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_banks.loc[f"{start_year}-01-01":].copy()

        
        data_filtered['Strategy_1_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1                                                                    
        Total_Return = data_filtered['Strategy_1_Return'].iloc[-1]                                                         
    
        # find sharpe ratio
        banks_1_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        banks_1_daily_mean = banks_1_daily.mean()
        banks_1_daily_std = banks_1_daily.std()
        if banks_1_daily_std != 0:
            sharpe = (banks_1_daily_mean/banks_1_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_1_Banks.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_1_Banks.loc[w, 'Return'] = Total_Return
        Strat_1_Banks.loc[w, 'Max_Drawdown'] = Max_Drawdown

        # takes column for each data measure -> ranks them from ideal to non ideal
        # takes rank and multiplies it by -> adds up 3 values for each window and ranks Ranking_Score from low to high
        # returns the window w/ the best performance (lowest overall Ranking_Score = top of list)
    Rankings_1_Banks['Sharpe_Rank'] = Strat_1_Banks['Sharpe'].rank(ascending=False)
    Rankings_1_Banks['Return_Rank'] = Strat_1_Banks['Return'].rank(ascending=False)
    Rankings_1_Banks['Drawdown_Rank'] = Strat_1_Banks['Max_Drawdown'].rank()
    Rankings_1_Banks['Final_Score'] = (
        (Rankings_1_Banks['Sharpe_Rank'])*(.4) +
        (Rankings_1_Banks['Return_Rank'])*(.4) +
        (Rankings_1_Banks['Drawdown_Rank'])*(.2)
        )
    Best_Window_1_Banks = Rankings_1_Banks['Final_Score'].idxmin()

    return Strat_1_Banks, Best_Window_1_Banks


def banks_strategy_2(window):

    data_banks = yf.download(banks, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_banks['Close'].copy()
    
    Strat_2_Banks = pd.DataFrame(index=windows_to_test)
    Rankings_2_Banks = pd.DataFrame(index=windows_to_test)

    for w in windows_to_test:

        data_banks = data_raw.copy()

        for t in banks:
            data_banks[f'{t}_Return_Window'] = data_banks[t].pct_change(w)
            data_banks[f'{t}_Daily_Return'] = data_banks[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in banks]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_banks = data_banks.dropna(subset=return_columns, how='all')
        
        # second highest
        data_banks['Second_Highest_Ticker'] = data_banks[return_columns].mask(data_banks[return_columns].apply(lambda x: x == x.max(), axis=1)).idxmax(axis=1)
        data_banks['just_the_ticker_2L'] = data_banks['Second_Highest_Ticker'].str.replace('_Return_Window', '')                 
        data_banks['Trade_Second_Highest'] = data_banks['just_the_ticker_2L'].shift(1)                                                             
        data_banks['Ticker_Second_Highest_Daily'] = data_banks.apply(lambda x: x[f"{x['Trade_Second_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Highest']) else 0, axis=1)

        # second lowest
        data_banks['Second_Lowest_Ticker'] = data_banks[return_columns].mask(data_banks[return_columns].apply(lambda x: x == x.min(), axis=1)).idxmin(axis=1)
        data_banks['just_the_ticker_2L'] = data_banks['Second_Lowest_Ticker'].str.replace('_Return_Window', '')                 
        data_banks['Trade_Second_Lowest'] = data_banks['just_the_ticker_2L'].shift(1)                                                             
        data_banks['Ticker_Second_Lowest_Daily'] = data_banks.apply(lambda x: x[f"{x['Trade_Second_Lowest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_banks['Short_Long_Strategy'] = data_banks['Ticker_Second_Highest_Daily']*(-1) + data_banks['Ticker_Second_Lowest_Daily']
        
        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_banks[data_banks.index.year >= start_year].copy()
        
        data_filtered['Strategy_2_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1
        Total_Return = data_filtered['Strategy_2_Return'].iloc[-1]                                                         

        # find sharpe ratio
        banks_2_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        banks_2_daily_mean = banks_2_daily.mean()
        banks_2_daily_std = banks_2_daily.std()
        if banks_2_daily_std != 0:
            sharpe = (banks_2_daily_mean/banks_2_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_2_Banks.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_2_Banks.loc[w, 'Return'] = Total_Return
        Strat_2_Banks.loc[w, 'Max_Drawdown'] = Max_Drawdown


    Rankings_2_Banks['Sharpe_Rank'] = Strat_2_Banks['Sharpe'].rank(ascending=False)
    Rankings_2_Banks['Return_Rank'] = Strat_2_Banks['Return'].rank(ascending=False)
    Rankings_2_Banks['Drawdown_Rank'] = Strat_2_Banks['Max_Drawdown'].rank()
    Rankings_2_Banks['Final_Score'] = (
        (Rankings_2_Banks['Sharpe_Rank'])*(.4) +
        (Rankings_2_Banks['Return_Rank'])*(.4) +
        (Rankings_2_Banks['Drawdown_Rank'])*(.2)
        )
    Best_Window_2_Banks = Rankings_2_Banks['Final_Score'].idxmin()

    return Strat_2_Banks, Best_Window_2_Banks



def oil_gas_strategy_1(window):

    data_oil_gas = yf.download(oil_gas, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_oil_gas['Close'].copy()

    Strat_1_Oil_Gas = pd.DataFrame(index=windows_to_test)
    Rankings_1_Oil_Gas = pd.DataFrame(index=windows_to_test)
    
    for w in windows_to_test:
        
        data_oil_gas = data_raw.copy()

        for t in oil_gas:
            data_oil_gas[f'{t}_Return_Window'] = data_oil_gas[t].pct_change(w)
            data_oil_gas[f'{t}_Daily_Return'] = data_oil_gas[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in oil_gas]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_oil_gas = data_oil_gas.dropna(subset=return_columns, how='all')

        # filters for ticker w/ highest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_oil_gas['Ticker_Highest'] = data_oil_gas[return_columns].idxmax(axis=1)
        data_oil_gas['just_the_ticker_H'] = data_oil_gas['Ticker_Highest'].str.replace('_Return_Window', '')                                                           
        data_oil_gas['Trade_Highest'] = data_oil_gas['just_the_ticker_H'].shift(1)
        data_oil_gas['Ticker_Highest_Daily'] = data_oil_gas.apply(lambda x: x[f"{x['Trade_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Highest']) else 0, axis=1)

        # filters for ticker w/ lowest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_oil_gas['Ticker_Lowest'] = data_oil_gas[return_columns].idxmin(axis=1)
        data_oil_gas['just_the_ticker_L'] = data_oil_gas['Ticker_Lowest'].str.replace('_Return_Window', '')                                                           
        data_oil_gas['Trade_Lowest'] = data_oil_gas['just_the_ticker_L'].shift(1)                                                               
        data_oil_gas['Ticker_Lowest_Daily'] = data_oil_gas.apply(lambda x: x[f"{x['Trade_Lowest']}_Daily_Return"]if pd.notnull(x['Trade_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_oil_gas['Short_Long_Strategy'] = data_oil_gas['Ticker_Highest_Daily']*(-1) + data_oil_gas['Ticker_Lowest_Daily']

        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_oil_gas.loc[f"{start_year}-01-01":].copy()

        
        data_filtered['Strategy_1_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1                                                                    
        Total_Return = data_filtered['Strategy_1_Return'].iloc[-1]                                                         
    
        # find sharpe ratio
        oil_gas_1_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        oil_gas_1_daily_mean = oil_gas_1_daily.mean()
        oil_gas_1_daily_std = oil_gas_1_daily.std()
        if oil_gas_1_daily_std != 0:
            sharpe = (oil_gas_1_daily_mean/oil_gas_1_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_1_Oil_Gas.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_1_Oil_Gas.loc[w, 'Return'] = Total_Return
        Strat_1_Oil_Gas.loc[w, 'Max_Drawdown'] = Max_Drawdown

        # takes column for each data measure -> ranks them from ideal to non ideal
        # takes rank and multiplies it by -> adds up 3 values for each window and ranks Ranking_Score from low to high
        # returns the window w/ the best performance (lowest overall Ranking_Score = top of list)
    Rankings_1_Oil_Gas['Sharpe_Rank'] = Strat_1_Oil_Gas['Sharpe'].rank(ascending=False)
    Rankings_1_Oil_Gas['Return_Rank'] = Strat_1_Oil_Gas['Return'].rank(ascending=False)
    Rankings_1_Oil_Gas['Drawdown_Rank'] = Strat_1_Oil_Gas['Max_Drawdown'].rank()
    Rankings_1_Oil_Gas['Final_Score'] = (
        (Rankings_1_Oil_Gas['Sharpe_Rank'])*(.4) +
        (Rankings_1_Oil_Gas['Return_Rank'])*(.4) +
        (Rankings_1_Oil_Gas['Drawdown_Rank'])*(.2)
        )
    Best_Window_1_Oil_Gas = Rankings_1_Oil_Gas['Final_Score'].idxmin()

    return Strat_1_Oil_Gas, Best_Window_1_Oil_Gas


def oil_gas_strategy_2(window):

    data_oil_gas = yf.download(oil_gas, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_oil_gas['Close'].copy()
    
    Strat_2_Oil_Gas = pd.DataFrame(index=windows_to_test)
    Rankings_2_Oil_Gas = pd.DataFrame(index=windows_to_test)

    for w in windows_to_test:

        data_oil_gas = data_raw.copy()

        for t in oil_gas:
            data_oil_gas[f'{t}_Return_Window'] = data_oil_gas[t].pct_change(w)
            data_oil_gas[f'{t}_Daily_Return'] = data_oil_gas[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in oil_gas]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_oil_gas = data_oil_gas.dropna(subset=return_columns, how='all')
        
        # second highest
        data_oil_gas['Second_Highest_Ticker'] = data_oil_gas[return_columns].mask(data_oil_gas[return_columns].apply(lambda x: x == x.max(), axis=1)).idxmax(axis=1)
        data_oil_gas['just_the_ticker_2L'] = data_oil_gas['Second_Highest_Ticker'].str.replace('_Return_Window', '')                 
        data_oil_gas['Trade_Second_Highest'] = data_oil_gas['just_the_ticker_2L'].shift(1)                                                             
        data_oil_gas['Ticker_Second_Highest_Daily'] = data_oil_gas.apply(lambda x: x[f"{x['Trade_Second_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Highest']) else 0, axis=1)

        # second lowest
        data_oil_gas['Second_Lowest_Ticker'] = data_oil_gas[return_columns].mask(data_oil_gas[return_columns].apply(lambda x: x == x.min(), axis=1)).idxmin(axis=1)
        data_oil_gas['just_the_ticker_2L'] = data_oil_gas['Second_Lowest_Ticker'].str.replace('_Return_Window', '')                 
        data_oil_gas['Trade_Second_Lowest'] = data_oil_gas['just_the_ticker_2L'].shift(1)                                                             
        data_oil_gas['Ticker_Second_Lowest_Daily'] = data_oil_gas.apply(lambda x: x[f"{x['Trade_Second_Lowest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_oil_gas['Short_Long_Strategy'] = data_oil_gas['Ticker_Second_Highest_Daily']*(-1) + data_oil_gas['Ticker_Second_Lowest_Daily']
        
        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_oil_gas[data_oil_gas.index.year >= start_year].copy()
        
        data_filtered['Strategy_2_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1
        Total_Return = data_filtered['Strategy_2_Return'].iloc[-1]                                                         

        # find sharpe ratio
        oil_gas_2_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        oil_gas_2_daily_mean = oil_gas_2_daily.mean()
        oil_gas_2_daily_std = oil_gas_2_daily.std()
        if oil_gas_2_daily_std != 0:
            sharpe = (oil_gas_2_daily_mean/oil_gas_2_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_2_Oil_Gas.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_2_Oil_Gas.loc[w, 'Return'] = Total_Return
        Strat_2_Oil_Gas.loc[w, 'Max_Drawdown'] = Max_Drawdown


    Rankings_2_Oil_Gas['Sharpe_Rank'] = Strat_2_Oil_Gas['Sharpe'].rank(ascending=False)
    Rankings_2_Oil_Gas['Return_Rank'] = Strat_2_Oil_Gas['Return'].rank(ascending=False)
    Rankings_2_Oil_Gas['Drawdown_Rank'] = Strat_2_Oil_Gas['Max_Drawdown'].rank()
    Rankings_2_Oil_Gas['Final_Score'] = (
        (Rankings_2_Oil_Gas['Sharpe_Rank'])*(.4) +
        (Rankings_2_Oil_Gas['Return_Rank'])*(.4) +
        (Rankings_2_Oil_Gas['Drawdown_Rank'])*(.2)
        )
    Best_Window_2_Oil_Gas = Rankings_2_Oil_Gas['Final_Score'].idxmin()

    return Strat_2_Oil_Gas, Best_Window_2_Oil_Gas



def homebuilders_strategy_1(window):

    data_homebuilders = yf.download(homebuilders, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_homebuilders['Close'].copy()

    Strat_1_Homebuilders = pd.DataFrame(index=windows_to_test)
    Rankings_1_Homebuilders = pd.DataFrame(index=windows_to_test)
    
    for w in windows_to_test:
        
        data_homebuilders = data_raw.copy()

        for t in homebuilders:
            data_homebuilders[f'{t}_Return_Window'] = data_homebuilders[t].pct_change(w)
            data_homebuilders[f'{t}_Daily_Return'] = data_homebuilders[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in homebuilders]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_homebuilders = data_homebuilders.dropna(subset=return_columns, how='all')

        # filters for ticker w/ highest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_homebuilders['Ticker_Highest'] = data_homebuilders[return_columns].idxmax(axis=1)
        data_homebuilders['just_the_ticker_H'] = data_homebuilders['Ticker_Highest'].str.replace('_Return_Window', '')                                                           
        data_homebuilders['Trade_Highest'] = data_homebuilders['just_the_ticker_H'].shift(1)
        data_homebuilders['Ticker_Highest_Daily'] = data_homebuilders.apply(lambda x: x[f"{x['Trade_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Highest']) else 0, axis=1)

        # filters for ticker w/ lowest return from window
        # finds daily return for that ticker (shifts 1 to "trade" the next day)
        data_homebuilders['Ticker_Lowest'] = data_homebuilders[return_columns].idxmin(axis=1)
        data_homebuilders['just_the_ticker_L'] = data_homebuilders['Ticker_Lowest'].str.replace('_Return_Window', '')                                                           
        data_homebuilders['Trade_Lowest'] = data_homebuilders['just_the_ticker_L'].shift(1)                                                               
        data_homebuilders['Ticker_Lowest_Daily'] = data_homebuilders.apply(lambda x: x[f"{x['Trade_Lowest']}_Daily_Return"]if pd.notnull(x['Trade_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_homebuilders['Short_Long_Strategy'] = data_homebuilders['Ticker_Highest_Daily']*(-1) + data_homebuilders['Ticker_Lowest_Daily']

        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_homebuilders.loc[f"{start_year}-01-01":].copy()

        
        data_filtered['Strategy_1_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1                                                                    
        Total_Return = data_filtered['Strategy_1_Return'].iloc[-1]                                                         
    
        # find sharpe ratio
        homebuilders_1_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        homebuilders_1_daily_mean = homebuilders_1_daily.mean()
        homebuilders_1_daily_std = homebuilders_1_daily.std()
        if homebuilders_1_daily_std != 0:
            sharpe = (homebuilders_1_daily_mean/homebuilders_1_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_1_Homebuilders.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_1_Homebuilders.loc[w, 'Return'] = Total_Return
        Strat_1_Homebuilders.loc[w, 'Max_Drawdown'] = Max_Drawdown

        # takes column for each data measure -> ranks them from ideal to non ideal
        # takes rank and multiplies it by -> adds up 3 values for each window and ranks Ranking_Score from low to high
        # returns the window w/ the best performance (lowest overall Ranking_Score = top of list)
    Rankings_1_Homebuilders['Sharpe_Rank'] = Strat_1_Homebuilders['Sharpe'].rank(ascending=False)
    Rankings_1_Homebuilders['Return_Rank'] = Strat_1_Homebuilders['Return'].rank(ascending=False)
    Rankings_1_Homebuilders['Drawdown_Rank'] = Strat_1_Homebuilders['Max_Drawdown'].rank()
    Rankings_1_Homebuilders['Final_Score'] = (
        (Rankings_1_Homebuilders['Sharpe_Rank'])*(.4) +
        (Rankings_1_Homebuilders['Return_Rank'])*(.4) +
        (Rankings_1_Homebuilders['Drawdown_Rank'])*(.2)
        )
    Best_Window_1_Homebuilders = Rankings_1_Homebuilders['Final_Score'].idxmin()

    return Strat_1_Homebuilders, Best_Window_1_Homebuilders


def homebuilders_strategy_2(window):

    data_homebuilders = yf.download(homebuilders, start=f"{data_start}-01-01",auto_adjust=True)
    data_raw = data_homebuilders['Close'].copy()
    
    Strat_2_Homebuilders = pd.DataFrame(index=windows_to_test)
    Rankings_2_Homebuilders = pd.DataFrame(index=windows_to_test)

    for w in windows_to_test:

        data_homebuilders = data_raw.copy()

        for t in homebuilders:
            data_homebuilders[f'{t}_Return_Window'] = data_homebuilders[t].pct_change(w)
            data_homebuilders[f'{t}_Daily_Return'] = data_homebuilders[t].pct_change(1)

        return_columns = [f"{t}_Return_Window" for t in homebuilders]

        # filters out the nan rows (bc it is an average of 20, so the first 19 are blank) - wouldnt that only matter for rolling?
        data_homebuilders = data_homebuilders.dropna(subset=return_columns, how='all')
        
        # second highest
        data_homebuilders['Second_Highest_Ticker'] = data_homebuilders[return_columns].mask(data_homebuilders[return_columns].apply(lambda x: x == x.max(), axis=1)).idxmax(axis=1)
        data_homebuilders['just_the_ticker_2L'] = data_homebuilders['Second_Highest_Ticker'].str.replace('_Return_Window', '')                 
        data_homebuilders['Trade_Second_Highest'] = data_homebuilders['just_the_ticker_2L'].shift(1)                                                             
        data_homebuilders['Ticker_Second_Highest_Daily'] = data_homebuilders.apply(lambda x: x[f"{x['Trade_Second_Highest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Highest']) else 0, axis=1)

        # second lowest
        data_homebuilders['Second_Lowest_Ticker'] = data_homebuilders[return_columns].mask(data_homebuilders[return_columns].apply(lambda x: x == x.min(), axis=1)).idxmin(axis=1)
        data_homebuilders['just_the_ticker_2L'] = data_homebuilders['Second_Lowest_Ticker'].str.replace('_Return_Window', '')                 
        data_homebuilders['Trade_Second_Lowest'] = data_homebuilders['just_the_ticker_2L'].shift(1)                                                             
        data_homebuilders['Ticker_Second_Lowest_Daily'] = data_homebuilders.apply(lambda x: x[f"{x['Trade_Second_Lowest']}_Daily_Return"] if pd.notnull(x['Trade_Second_Lowest']) else 0, axis=1)

        # finds return for long/short strategy
        data_homebuilders['Short_Long_Strategy'] = data_homebuilders['Ticker_Second_Highest_Daily']*(-1) + data_homebuilders['Ticker_Second_Lowest_Daily']
        
        # above this line -> finds data for desired period and a year before (to get a running start)
        # this line filters for desired period
        data_filtered = data_homebuilders[data_homebuilders.index.year >= start_year].copy()
        
        data_filtered['Strategy_2_Return'] = (1 + data_filtered['Short_Long_Strategy']).cumprod()-1
        Total_Return = data_filtered['Strategy_2_Return'].iloc[-1]                                                         

        # find sharpe ratio
        homebuilders_2_daily = data_filtered['Short_Long_Strategy'].fillna(0)
        homebuilders_2_daily_mean = homebuilders_2_daily.mean()
        homebuilders_2_daily_std = homebuilders_2_daily.std()
        if homebuilders_2_daily_std != 0:
            sharpe = (homebuilders_2_daily_mean/homebuilders_2_daily_std)*np.sqrt(252)
        else:
            sharpe = 0
        Sharpe_Ratio = sharpe

        # find max drawdown
        equity_curve = (1 + data_filtered['Short_Long_Strategy']).cumprod()
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        Max_Drawdown = drawdown.min()

        # sort the results (sharpe, return, max drawdown) -> want a ranking * weight = final ranking for strategy w/ window = x (the "best")
        Strat_2_Homebuilders.loc[w, 'Sharpe'] = Sharpe_Ratio
        Strat_2_Homebuilders.loc[w, 'Return'] = Total_Return
        Strat_2_Homebuilders.loc[w, 'Max_Drawdown'] = Max_Drawdown


    Rankings_2_Homebuilders['Sharpe_Rank'] = Strat_2_Homebuilders['Sharpe'].rank(ascending=False)
    Rankings_2_Homebuilders['Return_Rank'] = Strat_2_Homebuilders['Return'].rank(ascending=False)
    Rankings_2_Homebuilders['Drawdown_Rank'] = Strat_2_Homebuilders['Max_Drawdown'].rank()
    Rankings_2_Homebuilders['Final_Score'] = (
        (Rankings_2_Homebuilders['Sharpe_Rank'])*(.4) +
        (Rankings_2_Homebuilders['Return_Rank'])*(.4) +
        (Rankings_2_Homebuilders['Drawdown_Rank'])*(.2)
        )
    Best_Window_2_Homebuilders = Rankings_2_Homebuilders['Final_Score'].idxmin()

    return Strat_2_Homebuilders, Best_Window_2_Homebuilders

# work outside functions

# define array of window values
first_part = np.arange(10,55,5)
second_part = np.arange(60,130,10)
third_part = np.arange(140,220,20)
windows_to_test = np.concatenate([first_part, second_part, third_part])

# final matrix w/ 6 columns: will include 8 rows of info = (2 strategies) x (4 industries)
# represent the best versions of each strategy for each indsutry (only change is window)
# can rank these 8 versions to show best -> worst

Strat_1_Airlines, Best_Window_1_Airlines = airlines_strategy_1(windows_to_test)
Strat_2_Airlines, Best_Window_2_Airlines = airlines_strategy_2(windows_to_test)

Strat_1_Banks, Best_Window_1_Banks = banks_strategy_1(windows_to_test)
Strat_2_Banks, Best_Window_2_Banks = banks_strategy_2(windows_to_test)

Strat_1_Oil_Gas, Best_Window_1_Oil_Gas = oil_gas_strategy_1(windows_to_test)
Strat_2_Oil_Gas, Best_Window_2_Oil_Gas = oil_gas_strategy_2(windows_to_test)

Strat_1_Homebuilders, Best_Window_1_Homebuilders = homebuilders_strategy_1(windows_to_test)
Strat_2_Homebuilders, Best_Window_2_Homebuilders = homebuilders_strategy_2(windows_to_test)

# airlines
Optimal_Version = pd.DataFrame(columns = ['Industry', 'Strategy', 'Window', 'Sharpe', 'Return', 'Max Drawdown'])
Optimal_Version.loc[len(Optimal_Version)] = [
    'Airlines',
    '1',
    Best_Window_1_Airlines,
    round(Strat_1_Airlines.loc[Best_Window_1_Airlines, 'Sharpe'], 2),
    f"{round(Strat_1_Airlines.loc[Best_Window_1_Airlines, 'Return']*100, 2)}%",
    f"{round(Strat_1_Airlines.loc[Best_Window_1_Airlines, 'Max_Drawdown']*100, 2)}%",
    
    ]
                                           
Optimal_Version.loc[len(Optimal_Version)] = [
    'Airlines',
    '2',
    Best_Window_2_Airlines,
    round(Strat_2_Airlines.loc[Best_Window_2_Airlines, 'Sharpe'], 2),
    f"{round(Strat_2_Airlines.loc[Best_Window_2_Airlines, 'Return']*100, 2)}%",
    f"{round(Strat_2_Airlines.loc[Best_Window_2_Airlines, 'Max_Drawdown']*100, 2)}%",
    ]

# banks
Optimal_Version.loc[len(Optimal_Version)] = [
    'Banks',
    '1',
    Best_Window_1_Banks,
    round(Strat_1_Banks.loc[Best_Window_1_Banks, 'Sharpe'], 2),
    f"{round(Strat_1_Banks.loc[Best_Window_1_Banks, 'Return']*100, 2)}%",
    f"{round(Strat_1_Banks.loc[Best_Window_1_Banks, 'Max_Drawdown']*100, 2)}%",
    ]
                                           
Optimal_Version.loc[len(Optimal_Version)] = [
    'Banks',
    '2',
    Best_Window_2_Banks,
    round(Strat_2_Banks.loc[Best_Window_2_Banks, 'Sharpe'], 2),
    f"{round(Strat_2_Banks.loc[Best_Window_2_Banks, 'Return']*100, 2)}%",
    f"{round(Strat_2_Banks.loc[Best_Window_2_Banks, 'Max_Drawdown']*100, 2)}%",
    ]

# oil_gas
Optimal_Version.loc[len(Optimal_Version)] = [
    'Oil_Gas',
    '1',
    Best_Window_1_Oil_Gas,
    round(Strat_1_Oil_Gas.loc[Best_Window_1_Oil_Gas, 'Sharpe'], 2),
    f"{round(Strat_1_Oil_Gas.loc[Best_Window_1_Oil_Gas, 'Return']*100, 2)}%",
    f"{round(Strat_1_Oil_Gas.loc[Best_Window_1_Oil_Gas, 'Max_Drawdown']*100, 2)}%",
    ]
                                           
Optimal_Version.loc[len(Optimal_Version)] = [
    'Oil_Gas',
    '2',
    Best_Window_2_Oil_Gas,
    round(Strat_2_Oil_Gas.loc[Best_Window_2_Oil_Gas, 'Sharpe'], 2),
    f"{round(Strat_2_Oil_Gas.loc[Best_Window_2_Oil_Gas, 'Return']*100, 2)}%",
    f"{round(Strat_2_Oil_Gas.loc[Best_Window_2_Oil_Gas, 'Max_Drawdown']*100, 2)}%",
    ]

# homebuilders
Optimal_Version.loc[len(Optimal_Version)] = [
    'Homebuilders',
    '1',
    Best_Window_1_Homebuilders,
    round(Strat_1_Homebuilders.loc[Best_Window_1_Homebuilders, 'Sharpe'], 2),
    f"{round(Strat_1_Homebuilders.loc[Best_Window_1_Homebuilders, 'Return']*100, 2)}%",
    f"{round(Strat_1_Homebuilders.loc[Best_Window_1_Homebuilders, 'Max_Drawdown']*100, 2)}%",
    ]
                                           
Optimal_Version.loc[len(Optimal_Version)] = [
    'Homebuilders',
    '2',
    Best_Window_2_Homebuilders,
    round(Strat_2_Homebuilders.loc[Best_Window_2_Homebuilders, 'Sharpe'], 2),
    f"{round(Strat_2_Homebuilders.loc[Best_Window_2_Homebuilders, 'Return']*100, 2)}%",
    f"{round(Strat_2_Homebuilders.loc[Best_Window_2_Homebuilders, 'Max_Drawdown']*100, 2)}%",
    ]

Optimal_Version.to_csv(f'{start_year}-{end_year} Study.csv', index=False)
    



                                                          

    
    



