from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd

from data import DataNotFoundException, Frequency, QuoteData
from data.data import DataSource
from data.yahoo import YahooDataSource
from security import Security


class YahooBackTestDataSource(DataSource):
    def __init__(self, curr_date: datetime):
        self.data_source = YahooDataSource()
        self.curr_date = curr_date
        self.is_open = False

    def price_history(
        self,
        security: Security,
        frequency: Frequency = Frequency.DAY,
        bar_count: Optional[int] = None,
        approx_eod_close: bool = True,
    ) -> pd.DataFrame:
        assert frequency == Frequency.DAY, "Yahoo only supports daily data"
        data = self.data_source.price_history(security, frequency)
        data.sort_index(inplace=True, na_position="first")
        end_date = self.curr_date
        if not approx_eod_close:
            end_date -= timedelta(1)
        else:
            if self.is_open:
                # if we're at open, then set the close, high, and low to the open price
                print("Making copy")
                data = data.copy()
                open_price = data[self.curr_date]["Open"]
                data[self.curr_date][["Close", "High", "Low"]] = open_price
                data[self.curr_date]["Volume"] = 0
        return data[: self.curr_date][-bar_count:]

    def quote(self, security: Security) -> QuoteData:
        raise DataNotFoundException
