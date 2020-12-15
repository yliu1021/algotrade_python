from datetime import datetime


class QuoteData:
    """
    Quote data represents current data of the security such as the bid and ask spread
    and other current information (dividend, beta, etc.)

    Currently, only bid and ask is supported
    """

    def __init__(self, bid: float, ask: float, data_time: datetime):
        self.bid = bid
        self.ask = ask
        self.data_time = data_time
