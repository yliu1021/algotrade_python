from functools import reduce
from typing import List

import numpy as np
import pandas as pd

from broker.broker import Broker
from data.data import DataSource
from security import Equity
from strategy.strategy import OpenCloseStrategy
from strategy.util import get_pct_returns


class KellyCriterion(OpenCloseStrategy):
    def __init__(self, symbols: List[str]):
        self.symbols = list(map(Equity, symbols))

    def before_close(self, broker: Broker, data_source: DataSource):
        """
        buy and hold strategy
        :param broker:
        :param data_source:
        :return:
        """
        past_returns = get_pct_returns(self.symbols, "Close", 101, data_source)
        past_returns = past_returns.values
        c = np.cov(past_returns, rowvar=False)
        m = np.mean(past_returns, axis=0)
        weights = np.linalg.pinv(c) @ m / 2
        leverage = np.sum(np.abs(weights))
        if leverage > 2:
            weights = weights / leverage * 2
        for weight, symbol in zip(weights, self.symbols):
            assert not np.isnan(weight), "Can't have NaN weight"
            broker.place_order_proportion(symbol, weight)

    @property
    def name(self):
        return "Kelly Criterion"
