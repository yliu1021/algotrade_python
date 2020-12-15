from functools import reduce
from typing import List

import numpy as np
import pandas as pd
from scipy import stats

from broker.broker import Broker
from data.data import DataSource
from security import Equity
from strategy.strategy import OpenCloseStrategy
from strategy.util import get_pct_returns


class BuyHedgeSpy(OpenCloseStrategy):
    def __init__(self, symbols: List[str]):
        self.symbols = list(map(Equity, symbols))

    def before_close(self, broker: Broker, data_source: DataSource):
        """
        buy and hold strategy
        :param broker:
        :param data_source:
        :return:
        """
        bar_count = 100
        past_returns = get_pct_returns(self.symbols, "Close", bar_count, data_source)
        spy_returns = (
            data_source.price_history(Equity("SPY"), bar_count=bar_count)["Close"]
            .pct_change()
            .dropna()
        )
        hedge_weight = 0
        for symbol in self.symbols:
            beta = stats.linregress(spy_returns, past_returns[symbol.ticker])[0]
            hedge_weight -= beta
        weights = np.ones(len(self.symbols) + 1, dtype=np.float)
        for i, symbol in enumerate(self.symbols):
            weights[i] = 1
        weights[-1] = hedge_weight
        weights /= np.sum(np.abs(weights))
        for weight, symbol in zip(weights, self.symbols):
            broker.place_order_proportion(symbol, weight)
        broker.place_order_proportion(Equity("SPY"), weights[-1])

    @property
    def name(self):
        return "Buy and Hedge SPY"
