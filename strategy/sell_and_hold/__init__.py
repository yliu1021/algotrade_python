from typing import List

from broker.broker import Broker
from data.data import DataSource
from security import Equity
from strategy.strategy import OpenCloseStrategy


class SellAndHold(OpenCloseStrategy):
    def __init__(self, symbols: List[str]):
        self.symbols = list(map(Equity, symbols))

    def before_close(self, broker: Broker, data_source: DataSource):
        """
        buy and hold strategy
        :param broker:
        :param data_source:
        :return:
        """
        for symbol in self.symbols:
            broker.place_order_proportion(symbol, -1 / len(self.symbols))

    @property
    def name(self):
        return "Sell and Hold"
