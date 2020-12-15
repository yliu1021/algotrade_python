from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional

import pandas as pd

from data.quotedata import QuoteData
from security import Security


class Frequency(Enum):
    MINUTE = auto()
    DAY = auto()
    WEEK = auto()
    MONTH = auto()
    YEAR = auto()


class DataSource(ABC):
    @abstractmethod
    def price_history(
        self,
        security: Security,
        frequency: Frequency = Frequency.DAY,
        bar_count: Optional[int] = None,
        approx_eod_close: bool = True,
    ) -> pd.DataFrame:
        """
        Gets the price history of a security adjusted for dividends and splits.
        The index of the DataFrame is the timestamp of each bar.
        :param security: the security to get data for
        :param frequency: the frequency of the bars
        :param bar_count: the number of `frequency` to fetch (if None, fetch everything)
        :param approx_eod_close: if True, will use the current price to approximate the closing price
        and add the current day to the the history as if it has already passed.
        :return: a pandas DataFrame with keys "Open", "High", "Low", "Close", and "Volume"
        :raises DataNotFoundException: if the data cannot be retrieved
        """
        pass

    @abstractmethod
    def quote(self, security: Security) -> QuoteData:
        """
        Gets a current quote of a security
        :param security: the security to fetch data for
        :return: QuoteData: a QuoteData instance that represents a current quote
        :raises DataNotFoundException: if the data cannot be found
        """
        pass
