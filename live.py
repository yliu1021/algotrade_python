from data.yahoo import YahooDataSource, preload_symbols
from broker.transparent import TransparentBroker
from security.security import Equity
from strategy.strategy import OpenCloseStrategy
from strategy.pattern_matching import PatternMatching
from strategy.buy_and_hold import BuyAndHold


def get_strategy_positions(liquid_capital: float, strategy: OpenCloseStrategy) -> TransparentBroker:
    data_source = YahooDataSource()
    broker = TransparentBroker(liquid_capital, data_source)
    strategy.before_close(broker, data_source)
    return broker


def main():
    symbols = [
        # "SPY",
        "AAPL",
        "MSFT",
        "AMZN",
        "GOOGL",
        "FB",
        "BRK-B",
        # "SPG",
        # "APD",
        # "HSIC",
        # "RL",
        # "PVH",
    ]
    preload_symbols(symbols)

    # strategy = PatternMatching(
    #     symbols,
    #     look_back_window=153,
    #     match_window_length=5,
    # )
    strategy = BuyAndHold(
        symbols
    )
    broker = get_strategy_positions(51841, strategy)
    print(f"{strategy.name} positions")
    for symbol, quantity in broker.positions.items():
        print(f"{symbol.ticker}: {quantity}")
    print(f"${broker.liquid_value:.2f}")


if __name__ == "__main__":
    main()
