from abc import ABC, abstractmethod

from broker.broker import Broker
from data.data import DataSource


class OpenCloseStrategy(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    def on_open(self, broker: Broker, data_source: DataSource):
        """
        Called on market open to place trades
        :param broker: the broker to use to place orders
        :param data_source: the data source to get pricing and quotes
        """
        pass

    def before_close(self, broker: Broker, data_source: DataSource):
        """
        Called right before market close to place trades
        :param broker: the broker to use to place orders
        :param data_source: the data source to get pricing and quotes. Note that
        approx_eod_close can be used here to approximate the current trading day's closing price
        """
        pass
