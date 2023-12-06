# %%
import matplotlib
matplotlib.use('Agg')  # Set the backend
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm

# Original stocks
all_tickers = ['AAPL', 'MSFT', 'JPM', 'AMZN', 'GOOGL', 'BAC', 'WMT', 'V', 'MA', 'PG', 'UNH', 'T', 'INTC', 'VZ', 'CSCO', 'XOM', 'KO', 'CVX', 'PFE', 'HD', 'MCD', 'MRK', 'DIS', 'WFC', 'CMCSA', 'PEP', 'ORCL', 'C', 'BA', 'MMM', 'ABBV', 'AMGN', 'CAT', 'DHR', 'MDLZ', 'NKE', 'UPS', 'QCOM', 'GILD', 'AXP', 'USB', 'TMO', 'GS', 'LLY', 'HON', 'MO', 'GM', 'F', 'IBM', 'GE', 'AIG', 'ALL', 'ADP', 'BMY', 'COP', 'DUK', 'KHC', 'LMT', 'NOC', 'RTX', 'SBUX', 'SO', 'TGT', 'TXN', 'CVS', 'SYK', 'DE', 'GS', 'HUM', 'INTU', 'LOW', 'MET', 'MS', 'PRU', 'WBA', 'AMT', 'CHTR', 'CL', 'D', 'FIS', 'ITW', 'OXY', 'PNC', 'TFC', 'BKNG', 'CB', 'CI', 'ECL', 'ACN', 'MMC', 'PLD', 'SRE', 'TJX', 'TROW', 'UHS', 'VFC', 'WELL', 'ZTS', 'ADI', 'BLK', 'ADSK', 'CME', 'COF', 'COST', 'CVS', 'DAL', 'EBAY', 'EL', 'EXC', 'FDX', 'GD', 'GLW', 'HD', 'HPE', 'HPQ', 'IBM', 'JNJ', 'JPM', 'KMI', 'KMX', 'LUV', 'MA', 'MCK', 'MDT', 'MET', 'MMM', 'MO', 'MRK', 'MS', 'MSI', 'NEE', 'NFLX', 'NOC', 'NSC', 'NVDA', 'ORCL', 'PFE', 'PG', 'PGR', 'PM', 'PNC', 'PYPL', 'QCOM', 'RTX', 'SBUX', 'SLB', 'SO', 'SPGI', 'SYY', 'T', 'TGT', 'TJX', 'TMO', 'TRV', 'TSLA', 'TXN', 'UNH', 'UNP', 'UPS', 'USB', 'V', 'VZ', 'WBA', 'WFC', 'WMT', 'XOM']

# Download stock data
stocks = all_tickers + ['SPY']
stock_data = {stock: yf.download(stock, start="2013-11-10", end="2023-11-10") for stock in stocks}

# Data Cleaning
for stock, data in stock_data.items():
    data.dropna(inplace=True)
    stock_data[stock] = data['Adj Close']

# Data Organization
data_df = pd.DataFrame({stock: data for stock, data in stock_data.items()})

# Calculate annual volatility for each stock
annual_volatility = data_df.pct_change().std() * np.sqrt(252)

# Categorize stocks based on volatility
volatility_thresholds = annual_volatility.quantile([0.33, 0.66])
stable = annual_volatility[annual_volatility <= volatility_thresholds[0.33]].index.tolist()
middle = annual_volatility[(annual_volatility > volatility_thresholds[0.33]) & (annual_volatility <= volatility_thresholds[0.66])].index.tolist()
growth = annual_volatility[annual_volatility > volatility_thresholds[0.66]].index.tolist()

# Helper function to format currency
def format_currency(value):
    return "${:,.2f}".format(value)

# Function to calculate beta of a portfolio
def calculate_portfolio_beta(portfolio, market_data):
    portfolio_returns = data_df[portfolio].pct_change().dropna()
    market_returns = market_data.pct_change().dropna()

    # Aligning the lengths of the data
    min_length = min(len(portfolio_returns), len(market_returns))
    portfolio_returns = portfolio_returns[-min_length:]
    market_returns = market_returns[-min_length:]

    covariance_matrix = np.cov(portfolio_returns.values.T, market_returns.values)
    covariance = covariance_matrix[:len(portfolio), -1]
    market_variance = covariance_matrix[-1, -1]
    beta = covariance / market_variance
    return beta.mean()  # Average beta of the portfolio

# Portfolio Analysis Function with Visualization and Enhanced Metrics
def portfolio_analysis(portfolio, portfolio_name):
    portfolio_data = data_df[portfolio]
    investment_amount = 100 / len(portfolio)  # Equal distribution of $100

    # Past Performance
    initial_prices = portfolio_data.iloc[0]
    latest_prices = portfolio_data.iloc[-1]
    past_performance = ((latest_prices - initial_prices) / initial_prices * investment_amount).sum()

    # Visualization
    normalized_data = (portfolio_data / portfolio_data.iloc[0] * investment_amount).sum(axis=1)
    plt.figure(figsize=(10, 6))
    plt.plot(normalized_data, label=f"{portfolio_name} Portfolio")
    plt.title(f"Past Performance of {portfolio_name.capitalize()} Portfolio Over 10 Years")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"static/{portfolio_name}_portfolio_performance.png")
    plt.close()  # Close the plot to free up memory

    # Future Performance using CAPM
    risk_free_rate = 0.0461  # 4.61% as of 11/10/2023
    market_return = 0.0961  # Assumed market return of 9.61%
    beta = calculate_portfolio_beta(portfolio, data_df['SPY'])  # Using SPY as market index
    expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
    expected_future_performance = 100 * ((1 + expected_return) ** 10)

    # Results with plot
    return {
        'data': {
            'past_performance': format_currency(past_performance),
            'expected_future_performance': format_currency(expected_future_performance),
            'portfolio_beta': beta,

        },
        'explanation': {
            'past_performance': 'The past performance total represents the gain or loss if $100 was invested equally among the portfolio stocks 10 years ago. Past performance is not indicative of future results. The past performance is calculated using the adjusted closing prices of the portfolio stocks.',
            'expected_future_performance': 'The expected future performance total represents the projected total value of a $100 investment equally among the portfolio stocks over the next 10 years, based on CAPM. The risk-free rate is the 10-year Treasury yield as of 11/10/2023. The market return is assumed to be 9.61%. The CAPM formula is used to calculate the expected return of the portfolio. The expected return is then compounded over 10 years to calculate the expected future performance.',
            'portfolio_beta': 'The portfolio beta represents the average beta of the portfolio. Beta is a measure of the volatility of a portfolio compared to the market. A beta of 1 indicates that the portfolio is as volatile as the market. A beta of less than 1 indicates that the portfolio is less volatile than the market. A beta of greater than 1 indicates that the portfolio is more volatile than the market. Beta is calculated using the 10-year daily returns of the portfolio and the S&P 500. Additional education resources on all of the above topics can be found on Investopedia.',
        },
        'tickers': portfolio
    }

# Function to calculate portfolio performance
def calculate_portfolio_performance(profile_type):
    portfolio_map = {
        'aggressive': growth,
        'moderate': middle,
        'conservative': stable
    }
    portfolio = portfolio_map.get(profile_type, stable)
    return portfolio_analysis(portfolio, profile_type.capitalize())

# Example Usage
result = calculate_portfolio_performance('moderate')