from functools import reduce
from typing import List, Union

import pandas as pd

from data.data import DataSource
from security import Equity


def get_pct_returns(
    symbols: List[Union[str, Equity]],
    field: str,
    bar_count: int,
    data_source: DataSource,
):
    symbols = [Equity(s) if isinstance(s, str) else s for s in symbols]
    prices = [
        data_source.price_history(symbol, bar_count=bar_count, approx_eod_close=True)[
            field
        ].pct_change()
        for symbol in symbols
    ]
    for price, symbol in zip(prices, symbols):
        price.name = symbol.ticker
    past_returns = reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how="outer"
        ),
        prices,
    )
    past_returns.dropna(inplace=True)
    return past_returns
