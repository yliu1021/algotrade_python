from enum import Enum, auto


class SecurityType(Enum):
    EQUITY = auto()  # a stock or share in a company


class Security:
    def __init__(self, ticker: str, security_type: SecurityType):
        self.ticker = ticker
        self.type = security_type

    def __hash__(self):
        return hash(self.ticker)

    def __eq__(self, other):
        return isinstance(other, Security) and self.ticker == other.ticker

    def __ne__(self, other):
        return not (self == other)


class Equity(Security):
    def __init__(self, ticker: str):
        super().__init__(ticker, SecurityType.EQUITY)
