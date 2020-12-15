from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from skopt import gp_minimize
from skopt.space.space import Integer, Real

from data.yahoo import preload_symbols
from strategy.pattern_matching import PatternMatching
from trading_environments import backtest_environment

symbols = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "FB",
    "BRK-B",
]
preload_symbols(symbols)


def optimize(args):
    look_back_window = int(round(args[0]))
    match_window_length = int(round(args[1]))

    start_date = datetime(2020, 4, 1)
    end_date = datetime(2020, 12, 1)

    print(
        "Trying with:",
        look_back_window,
        match_window_length,
    )

    try:
        ts = backtest_environment.run_open_close(
            PatternMatching(
                symbols,
                look_back_window=look_back_window,
                match_window_length=match_window_length,
            ),
            50000,
            start_date,
            end_date,
            log=False,
            plot_metrics=False,
        )
    except Exception as e:
        print(e)
        return 0

    avg_sharpe = ts["Portfolio Sharpe Ratio"].mean()
    cumulative_returns = ts["Portfolio Cumulative Returns"][-1] + 1
    if np.isnan(avg_sharpe):
        avg_sharpe = 0
    if np.isnan(cumulative_returns):
        cumulative_returns = 0
    print(f"Sharpe: {avg_sharpe:.3f} Returns: {cumulative_returns-1:.3f}")
    # return -avg_sharpe * cumulative_returns
    return -cumulative_returns / ts["Portfolio Daily Returns"].std()


def main():
    opt_res = gp_minimize(
        optimize,
        [
            Integer(20, 200),
            Integer(5, 90),
        ],
        verbose=True,
        n_jobs=-1,
        n_calls=3000,
    )
    opt_x = opt_res.x
    fun = opt_res.fun
    x_iters = opt_res.x_iters
    func_vals = opt_res.func_vals
    print(f"Optimal found at {opt_x} with value: {fun}")
    print(x_iters)
    print(func_vals)
    plt.plot(np.arange(len(func_vals)), func_vals)
    plt.title("Optimization Progress")
    plt.show()


if __name__ == "__main__":
    main()
