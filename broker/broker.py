from abc import ABC, abstractmethod

from security import Security


class Broker(ABC):
    """
    An abstract base class for a broker. A broker is any class that can place trades on securities
    and keep track of capital.
    """

    @abstractmethod
    def place_order(self, symbol: Security, quantity: int):
        """
        Places a market order on `symbol` for `quantity`
        :param symbol: an instance of the `Symbol` class
        :param quantity: any integer (positive or negative)
        """
        pass

    @abstractmethod
    def place_limit_order(self, symbol: Security, quantity: int, limit_price: float):
        """
        Places a limit order on `symbol` for `quantity`
        :param symbol: an instance of the `Symbol` class
        :param quantity: any integer (positive or negative)
        :param limit_price: the limit price to place the order
        """
        pass

    @abstractmethod
    def place_order_proportion(self, symbol: Security, proportion: float):
        """
        Places a market order for `symbol` that will occupy `proportion` of the current capital
        :param symbol: an instance of the `Symbol` class
        :param proportion: the relative value to order compared to our current capital.
        A value of 1 means to spend our entire capital on `symbol`. Negative values represents shorting.
        Note that if the proportion is greater than 1, then we will attempt to use margin to leverage
        our position.
        """
        pass

    @abstractmethod
    def place_limit_order_proportion(
        self, symbol: Security, proportion: float, limit_price: float
    ):
        """
        Places a limit order for `symbol` that will occupy `proportion` of the current capital
        :param symbol: an instance of the `Symbol` class
        :param proportion: the relative value to order compared to our current capital.
        A value of 1 means to spend our entire capital on `symbol`. Negative values represents shorting.
        Note that if the proportion is greater than 1, then we will attempt to use margin to leverage
        our position.
        :param limit_price: the limit price to place the order
        """
        pass

    @property
    @abstractmethod
    def liquid_value(self) -> float:
        """
        Returns the amount of cash available in the account
        :return:
        """
        pass

    @property
    @abstractmethod
    def total_value(self) -> float:
        """
        Returns the total value of the portfolio plus the liquid value
        :return:
        """
        pass
