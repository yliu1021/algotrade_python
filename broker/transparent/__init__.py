import math
from collections import defaultdict

from broker.broker import Broker
from data.data import DataSource
from security import Security


class TransparentBroker(Broker):
    @property
    def liquid_value(self) -> float:
        return self.liquid_capital

    @property
    def total_value(self) -> float:
        return self.get_portfolio_value()

    def __init__(self, initial_capital: float, data_source: DataSource):
        self.liquid_capital = initial_capital
        self.positions = defaultdict(int)
        self._data_source = data_source

    def place_order(self, symbol: Security, quantity: int):
        price = self._get_curr_price(symbol)
        cost = price * quantity
        self.liquid_capital -= cost
        # self.liquid_capital -= abs(quantity) * 0.02  # add slippage
        self.positions[symbol] += quantity

    def place_limit_order(self, symbol: Security, quantity: int, limit_price: float):
        self.place_order(symbol, quantity)

    def place_order_proportion(self, symbol: Security, proportion: float):
        price = self._get_curr_price(symbol)
        portfolio_value = self.get_portfolio_value()
        stock_value = portfolio_value * proportion
        if math.isnan(price) or math.isnan(stock_value):
            quantity = 0
        else:
            quantity = int(round(stock_value / price)) - self.positions[symbol]
        self.place_order(symbol, quantity)

    def place_limit_order_proportion(
        self, symbol: Security, proportion: float, limit_price: float
    ):
        self.place_order_proportion(symbol, proportion)

    def _get_curr_price(self, symbol: Security) -> float:
        price = self._data_source.price_history(
            symbol, bar_count=1, approx_eod_close=True
        ).iloc[-1]["Close"]
        return price

    def get_portfolio_value(self) -> float:
        total_value = self.liquid_capital
        for symbol, quantity in self.positions.items():
            price = self._get_curr_price(symbol)
            total_value += price * quantity
        return total_value
