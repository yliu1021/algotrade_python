import math
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

from broker.transparent import TransparentBroker
from data.yahoo import YahooDataSource
from data.yahoobacktest import YahooBackTestDataSource
from security import Equity
from strategy.strategy import OpenCloseStrategy


def run_open_close(
    strategy: OpenCloseStrategy,
    initial_capital: float,
    start_date: datetime,
    end_date: datetime,
    benchmark: Equity = Equity("SPY"),
    plot_metrics: bool = True,
    log: bool = True,
) -> pd.DataFrame:
    yahoo_datasource = YahooDataSource()

    # Get the first valid trading day since start_date
    trading_days = yahoo_datasource.price_history(Equity("SPY")).index
    start_index = 0
    for start_index, trading_day in enumerate(trading_days):
        if trading_day >= start_date:
            break

    # Broker & Data Source
    data_source = YahooBackTestDataSource(trading_days[start_index])
    broker = TransparentBroker(initial_capital, data_source)

    # Metrics
    active_trading_days = list()
    portfolio_value = list()

    # Start Trading
    if log:
        print("Starting trades")
    for date_index in range(start_index, len(trading_days)):
        curr_day = trading_days[date_index]
        if curr_day > end_date:
            break

        if log:
            if date_index % 50 == 0:
                print(f"Trading on day: {curr_day}")

        data_source.curr_date = curr_day

        data_source.is_open = True
        strategy.on_open(broker, data_source)
        data_source.is_open = False
        strategy.before_close(broker, data_source)

        active_trading_days.append(curr_day)
        portfolio_value.append(broker.get_portfolio_value())

    if log:
        print("Done trading")
        print("Final Positions:")
        for symbol, quantity in broker.positions.items():
            print(f"\t{symbol.ticker}: {quantity}")
        print(f"Final Portfolio Value: ${broker.get_portfolio_value():.2f}")
        print(f"Portfolio Liquid Capital: ${broker.liquid_capital:.2f}")

    if log:
        print("Calculating tear sheet")
    tear_sheet = pd.DataFrame(index=active_trading_days)
    benchmark_value = yahoo_datasource.price_history(benchmark)[start_date:end_date][
        "Close"
    ]
    tear_sheet["Portfolio Value"] = portfolio_value
    tear_sheet["Benchmark Value"] = benchmark_value

    tear_sheet["Portfolio Cumulative Returns"] = (
        tear_sheet["Portfolio Value"] / tear_sheet["Portfolio Value"][0] - 1
    )
    tear_sheet["Benchmark Cumulative Returns"] = (
        tear_sheet["Benchmark Value"] / tear_sheet["Benchmark Value"][0] - 1
    )

    tear_sheet["Portfolio Daily Returns"] = tear_sheet["Portfolio Value"].pct_change()
    tear_sheet["Benchmark Daily Returns"] = tear_sheet["Benchmark Value"].pct_change()

    time_period = 180
    risk_free_rate = (1 + 0.12 / 100)**(1 / 252) - 1
    tear_sheet["Portfolio Sharpe Ratio"] = (
        tear_sheet["Portfolio Daily Returns"]
        .rolling(time_period)
        .apply(lambda x: (x.mean() - risk_free_rate) / x.std(), raw=True)
    ) * math.sqrt(252)
    tear_sheet["Benchmark Sharpe Ratio"] = (
        tear_sheet["Benchmark Daily Returns"]
        .rolling(time_period)
        .apply(lambda x: (x.mean() - risk_free_rate) / x.std(), raw=True)
    ) * math.sqrt(252)

    if plot_metrics:
        if log:
            print("Plotting metrics")
        fig, axs = plt.subplots(2, 2)
        fig.set_size_inches(10, 10)
        fig.suptitle(strategy.name, fontsize=16)

        # Plot portfolio vs benchmark cumulative returns
        tear_sheet["Portfolio Cumulative Returns"].plot(ax=axs[0, 0])
        tear_sheet["Benchmark Cumulative Returns"].plot(ax=axs[0, 0])
        portfolio_cumulative_returns = tear_sheet["Portfolio Cumulative Returns"][-1]
        benchmark_cumulative_returns = tear_sheet["Benchmark Cumulative Returns"][-1]
        axs[0, 0].legend(
            [
                f"Portfolio cumulative returns: {portfolio_cumulative_returns:.3f}",
                f"Benchmark cumulative returns: {benchmark_cumulative_returns:.3f}",
            ]
        )
        axs[0, 0].set_title("Cumulative Returns")

        # Plot estimated portfolio annual returns
        annual_returns = (
            tear_sheet["Portfolio Daily Returns"]
            .dropna()
            .expanding(180)
            .apply(lambda x: (1 + x.mean()) ** 252 - 1, raw=True)
        )
        annual_returns.name = "Estimated Annual Returns"
        annual_returns.dropna(inplace=True)
        annual_returns.plot(ax=axs[0, 1])
        axs[0, 1].legend([f"Average: {annual_returns.mean():.3f}"])
        axs[0, 1].set_title("Estimated Annual Returns")

        # Plot portfolio vs benchmark daily returns
        beta, alpha, corr_coef, p_val, stderr = stats.linregress(
            tear_sheet["Benchmark Daily Returns"].dropna(),
            tear_sheet["Portfolio Daily Returns"].dropna(),
        )
        sns.regplot(
            x=tear_sheet["Benchmark Daily Returns"],
            y=tear_sheet["Portfolio Daily Returns"],
            ax=axs[1, 0],
        )
        axs[1, 0].set_title("Daily Returns")
        axs[1, 0].legend(
            [
                f"β = {beta:.3f}, α = {alpha:.3f}, r^2 = {corr_coef**2:.3f}, p = {p_val:.3f}, std err = {stderr:.3f}",
            ]
        )

        # Plot portfolio and benchmark Sharpe ratios
        tear_sheet["Portfolio Sharpe Ratio"].plot(ax=axs[1, 1])
        tear_sheet["Benchmark Sharpe Ratio"].plot(ax=axs[1, 1])
        portfolio_avg_sr = tear_sheet["Portfolio Sharpe Ratio"].mean()
        benchmark_avg_sr = tear_sheet["Benchmark Sharpe Ratio"].mean()
        portfolio_total_sharpe = tear_sheet["Portfolio Sharpe Ratio"][-1]
        benchmark_total_sharpe = tear_sheet["Benchmark Sharpe Ratio"][-1]
        axs[1, 1].legend(
            [
                f"Portfolio avg SR: {portfolio_avg_sr:.3f} - Final: {portfolio_total_sharpe:.3f}",
                f"Benchmark avg SR: {benchmark_avg_sr:.3f} - Final: {benchmark_total_sharpe:.3f}",
            ]
        )
        axs[1, 1].set_title("Sharpe Ratio")

        plt.show()

    return tear_sheet
