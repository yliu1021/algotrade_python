from typing import List

import numpy as np

from broker.broker import Broker
from data.data import DataSource
from security import Equity
from strategy.strategy import OpenCloseStrategy
from strategy.util import get_pct_returns


class RunningAvg(OpenCloseStrategy):
    def __init__(self, symbols: List[str]):
        self.symbols = list(map(Equity, symbols))

    def before_close(self, broker: Broker, data_source: DataSource):
        """
        buy and hold strategy
        :param broker:
        :param data_source:
        :return:
        """
        past_returns = get_pct_returns(self.symbols, "Close", 10, data_source)
        print(past_returns)
        m = past_returns.mean().values
        weights = m / (np.sum(m) + 0.0001)
        for w in weights:
            print(f"{w:.4f}", end=" ")
        print()
        for weight, symbol in zip(weights, self.symbols):
            assert not np.isnan(weight), "Can't have NaN weight"
            broker.place_order_proportion(symbol, weight)

    @property
    def name(self):
        return "Running Avg"
