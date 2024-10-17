from utils import get_data_type, get_snapshot



class Frame:
    def __init__(self, api=None, snapshot_init=False, code=None, category=None):
        # common attributes
        self.api = api
        self.code = None
        self.data_type = None
        self.category = None
        self.timestamp = None
        self.simtrade = None
        self.is_snapshot = None

        # tick attributes
        self.price = None

        # bidask attributes
        self.best_bid = None
        self.best_ask = None

        # future option attributes
        self.underlying_price = None

        # Other attributes
        self.close = None
        self.price_pct_chg = None
        self.bid_pct_chg = None
        self.ask_pct_chg = None

        if snapshot_init:
            if api is None:
                raise ValueError("API is required for snapshot initialization")
            if code is None:
                raise ValueError("Code is required for snapshot initialization")
            if category is None:
                raise ValueError("Category is required for snapshot initialization")
            snapshot = get_snapshot(api, code, category)
            self.data_to_frame(snapshot)

    def data_to_frame(self, data):
        self.code = data.code
        data_type, category = get_data_type(data)
        self.data_type = data_type
        self.category = category
        self.timestamp = data.timestamp
        self.simtrade = data.simtrade
        if category == 'fop':
            self.underlying_price = data.underlying_price
        if data_type == 'snapshot':
            self.is_snapshot = True
        else:
            self.is_snapshot = False
        if data_type == 'tick':
            self._tick_to_frame(data)
        if data_type == 'bidask':
            self._bidask_to_frame(data)
        if data_type == 'quote':
            self._quote_to_frame(data)

    def _tick_to_frame(self, tick):
        self.price = tick.close
        self.update_pct()

    def _bidask_to_frame(self, bidask):
        self.best_bid = bidask.bid_price[0]
        self.best_ask = bidask.ask_price[0]
    
    def _quote_to_frame(self, quote):
        self._tick_to_frame(quote)
        self._bidask_to_frame(quote)

    def update_pct_chg(self):
        if self.close is not None:
            self.price_pct_chg = (self.price - self.close) / self.close * 100
            if self.best_bid is not None:
                self.bid_pct_chg = (self.best_bid - self.close) / self.close * 100
            if self.best_ask is not None:
                self.ask_pct_chg = (self.best_ask - self.close) / self.close * 100
    
    def update_close(self):
        raise NotImplementedError("Method update_close is not implemented")