from datetime import datetime

from data.yahoo import preload_symbols
from strategy.buy_and_hold import BuyAndHold
from strategy.pattern_matching import PatternMatching
from strategy.running_avg import RunningAvg
from strategy.kelly_criterion import KellyCriterion
from trading_environments import backtest_environment


def main():
    symbols = [
        # "SPY",
        "AAPL",
        "AMZN",
        "BRK-B",
        "FB",
        "GOOGL",
        "MSFT",
    ]

    start_date = datetime(2019, 1, 1)
    end_date = datetime(2020, 7, 1)
    preload_symbols(symbols)

    tear_sheet = backtest_environment.run_open_close(
        PatternMatching(
            symbols,
            look_back_window=500,
            match_window_length=50,
        ),
        50000,
        start_date,
        end_date,
    )

    # tear_sheet = backtest_environment.run_open_close(
    #     KellyCriterion(symbols),
    #     50000,
    #     start_date,
    #     end_date,
    # )

    portfolio_cum_returns = tear_sheet["Portfolio Cumulative Returns"] + 1
    portfolio_max_returns = portfolio_cum_returns.cummax()
    benchmark_cum_returns = tear_sheet["Benchmark Cumulative Returns"] + 1
    benchmark_max_returns = benchmark_cum_returns.cummax()

    draw_down = (portfolio_cum_returns - portfolio_max_returns) / portfolio_max_returns
    draw_down[draw_down == float('-inf')] = 0
    print(draw_down.min())
    draw_down = (benchmark_cum_returns - benchmark_max_returns) / benchmark_max_returns
    draw_down[draw_down == float('-inf')] = 0
    print(draw_down.min())


if __name__ == "__main__":
    main()
