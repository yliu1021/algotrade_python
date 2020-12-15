from typing import List

import numpy as np
import pandas as pd

from broker.broker import Broker
from data.data import DataSource
from security import Equity
from strategy.strategy import OpenCloseStrategy
from strategy.util import get_pct_returns


class PatternMatching(OpenCloseStrategy):
    def __init__(
        self, symbols: List[str], look_back_window: int, match_window_length: int
    ):
        self.symbols = list(map(Equity, symbols))
        self.look_back_window = look_back_window
        self.match_window_length = match_window_length

    def before_close(self, broker: Broker, data_source: DataSource):
        """
        pattern matching strategy
        :param broker:
        :param data_source:
        :return:
        """
        bar_count = self.look_back_window
        past_returns = get_pct_returns(self.symbols, "Close", bar_count, data_source)
        future_returns = list()

        match_length = self.match_window_length
        curr_returns = past_returns.iloc[-match_length:].values.flatten()
        match_scores = list()
        for i in range(len(past_returns) - 1, match_length - 1, -1):
            past_return_window = past_returns.iloc[
                i - match_length : i
            ].values.flatten()
            match_score = np.dot(curr_returns, past_return_window)
            match_score /= np.linalg.norm(curr_returns) * np.linalg.norm(
                past_return_window
            )
            if match_score > 0:
                match_scores.append(match_score**2)
                future_returns.append(past_returns.iloc[i].values)

        match_scores = np.array(match_scores) ** 2
        match_scores /= np.sum(match_scores)
        future_returns = np.array(future_returns)

        mean = np.sum(future_returns * match_scores[:, None], axis=0)
        cov = np.cov(future_returns, ddof=0, rowvar=False, aweights=match_scores)
        cov_inv = np.linalg.pinv(cov)
        weights = cov_inv @ mean
        max_weight = np.max(np.abs(weights))
        if max_weight > 2:
            weights /= max_weight
        # weights /= np.sum(np.abs(weights))
        for weight, symbol in zip(weights, self.symbols):
            assert not np.isnan(weight), "Can't have NaN weight"
            broker.place_order_proportion(symbol, weight)

    @property
    def name(self):
        return "Pattern Matching"
