# Multi-Industry Momentum & Reversion Backtester

This repository contains a comprehensive vectorized backtesting engine designed to analyze and rank long/short equity strategies across four distinct sectors: **Airlines, Banks, Oil & Gas, and Homebuilders**. The tool systematically iterates through various look-back windows to identify optimal parameters for capturing mean reversion and relative strength within specific industries.


## Features


* **Multi-Sector Strategy Analysis:** Built-in coverage for 24 specific tickers across four major industrial sectors, allowing for a comparative study of how different market segments respond to the same momentum/reversion signals.

* **Dual-Strategy Backtesting:**

* * **Strategy 1 (Extreme Extremes):** Shorts the best performer and longs the worst performer over a specific window.

* * **Strategy 2 (Second-Tier Extremes):** Targets the "second-best" and "second-worst" performers to avoid potential outlier noise or idiosyncratic events.

* **Dynamic Parameter Optimization:** Tests a wide range of look-back windows (from 10-day short-term to 220-day long-term) to find the most robust settings for each strategy.

* **Automated Scoring System:** Ranks strategy performance using a weighted scoring model that balances risk and reward, rather than focusing solely on raw returns.

* **Comprehensive Performance Metrics:** Calculates the **Sharpe Ratio, Total Cumulative Return**, and **Maximum Drawdown** for every tested iteration.

## Built With

* **Python 3.x:** The core programming language.

* **Pandas:** Extensively used for vectorized data manipulation and time-series alignment.

* **NumPy:** Employed for high-performance mathematical operations and array management.

* **yfinance:** Used for fetching real-time and historical market data directly from Yahoo Finance.


## Key Achievements in Code


**1. Efficient Vectorized Look-back Testing**

Instead of utilizing slow loops to simulate trades day-by-day, the engine uses vectorized operations via Pandas. By utilizing `.pct_change(w)` and `.idxmax()`, the script evaluates hundreds of look-back windows and thousands of data points in seconds, making the backtester highly scalable.

**2. Robust Weight-Based Ranking Logic**

The code implements a sophisticated `Final_Score` logic that prevents "overfitting" for high returns. By applying a weighted rank:

$$Score = (\text{Sharpe Rank} \times 0.4) + (\text{Return Rank} \times 0.4) + (\text{Drawdown Rank} \times 0.2)$$

The model identifies the most stable "Optimal Version" of a strategy, prioritizing risk-adjusted returns (Sharpe) and capital preservation (Drawdown) alongside profitability.

**3. Sophisticated Outlier Handling (Strategy 2)**

The implementation of Strategy 2 demonstrates advanced data masking. By using `.mask()` in conjunction with `.idxmax()` and `.idxmin()`, the code elegantly identifies the second-highest and second-lowest performers without the need for complex sorting or nested loops:

```
Python

data_airlines[return_columns].mask(data_airlines[return_columns].apply(lambda x: x == x.max(), axis=1)).idxmax(axis=1)
```

This ensures the strategy remains focused on broader industry trends rather than being skewed by single-stock anomalies.
