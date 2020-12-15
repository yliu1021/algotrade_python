# Algorithmic Trading with Python

## Getting Started
1. ```pip install -r requirements.txt```
2. ```python backtest.py```
3. ???
4. Profit

## Project Structure
```backtest.py```

This is the backtest file and probably the most important file.

```optimize.py```

This is similar to the backtest script but it's used to optimize strategy parameters (using Bayesian optimization via
`skopt`)

```live.py```

This is for trading live orders (basically `backtest.py` but with current prices).
It prints the positions onto the screen for the trader to place into whatever broker
they use.

```strategy/```

This package stores all the strategies that can be used. In this package, each strategy
is defined as its own module.

Creating your own strategy is simple. Just copy and paste any of the current strategies into
its own module and go from there.

```broker/```
```data/```
```security/```
```trading_environments/```

These are all helper packages used to make backtesting and live trading possible.