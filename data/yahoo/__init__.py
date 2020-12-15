from datetime import datetime
from typing import List, Optional

import pandas as pd
import yfinance as yf

from data import DataNotFoundException, Frequency, QuoteData
from data.data import DataSource
from security import Security, SecurityType

_cache = dict()


def preload_symbols(symbols: List[str]):
    symbols = list(map(lambda x: x.replace(".", "-"), symbols))
    data = yf.download(symbols, auto_adjust=True, progress=True, threads=True)
    data.sort_index(inplace=True, na_position="first")
    if isinstance(data.columns, pd.MultiIndex):
        data = data.reorder_levels([1, 0], axis=1)
        for symbol in symbols:
            _cache[symbol] = (data[symbol], datetime.now())
    else:
        _cache[symbols[0]] = (data, datetime.now())


class YahooDataSource(DataSource):
    def __init__(self):
        pass

    def price_history(
        self,
        security: Security,
        frequency: Frequency = Frequency.DAY,
        bar_count: Optional[int] = None,
        approx_eod_close: bool = False,
    ) -> pd.DataFrame:
        if security.type != SecurityType.EQUITY:
            raise ValueError(
                "Yahoo finance only support price history on Equity securities"
            )
        if frequency != Frequency.DAY:
            raise ValueError("Yahoo data source only provides daily data")
        if bar_count is not None:
            assert bar_count > 0, "Must request a positive number of bar data"
        else:
            bar_count = 0

        data = None
        # if data is cached return that
        if security.ticker in _cache:
            cached_data, cache_time = _cache[security.ticker]
            if self._fresh_cache(cache_time):
                data = cached_data
            else:
                del _cache[security.ticker]
        # if no cached data is found or if data is stale
        if data is None:
            # download from Yahoo finance
            print(f"Downloading data for {security.ticker}")
            data = yf.download(security.ticker, auto_adjust=True, progress=True)
            data.sort_index(inplace=True, na_position="first")
            _cache[security.ticker] = (data, datetime.now())
        return data.iloc[-bar_count:]

    def quote(self, security: Security) -> QuoteData:
        raise DataNotFoundException("Quote data not available on Yahoo finance")

    @staticmethod
    def _load_from_metadata(metadata) -> pd.DataFrame:
        cache_loc = metadata["cacheLocation"]
        return pd.read_csv(cache_loc)

    @staticmethod
    def _fresh_cache(last_refresh: datetime) -> bool:
        return datetime.today().date() == last_refresh.date()
