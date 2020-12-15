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


class Markov(OpenCloseStrategy):
    def __init__(
        self,
        symbols: List[str],
        look_back_window: int = 200,
        match_window_length: int = 2,
        match_threshold: float = 0.7,
        min_matches_threshold: int = 5,
    ):
        self.symbols = list(map(Equity, symbols))
        self.look_back_window = look_back_window
        self.match_window_length = match_window_length
        self.match_threshold = match_threshold
        self.min_matches_threshold = min_matches_threshold
        assert (
            self.min_matches_threshold >= 2
        ), "Must have at least 2 matches to calculate covariance matrix"

    def before_close(self, broker: Broker, data_source: DataSource):
        """
        buy and hold strategy
        :param broker:
        :param data_source:
        :return:
        """
        bar_count = self.look_back_window
        past_returns = get_pct_returns(self.symbols, "Close", bar_count, data_source)
        future_returns = list()

        match_length = self.match_window_length
        curr_returns = past_returns.iloc[-match_length:].values.flatten()
        for i in range(len(past_returns) - 1, match_length - 1, -1):
            past_return_window = past_returns.iloc[
                i - match_length : i
            ].values.flatten()
            match_score = np.dot(curr_returns, past_return_window)
            match_score /= np.linalg.norm(curr_returns) * np.linalg.norm(
                past_return_window
            )
            if match_score > self.match_threshold:
                future_returns.append(past_returns.iloc[i])
        future_returns = pd.DataFrame(future_returns)
        if len(future_returns) < self.min_matches_threshold:
            weights = np.zeros((len(past_returns.columns),), dtype=np.float)
        else:
            m = future_returns.mean().values
            cov_inv = np.linalg.pinv(future_returns.cov().values)
            weights = cov_inv @ m
            weights /= np.sum(np.abs(weights)) / 4
            # weights *= 2
            # debit = np.sum(weights) / 2
            # debit_weights = (1 - debit) / len(weights)
            # weights += debit_weights
        for weight, symbol in zip(weights, self.symbols):
            assert not np.isnan(weight), "Can't have NaN weight"
            broker.place_order_proportion(symbol, weight)

    @property
    def name(self):
        return "Markov"
