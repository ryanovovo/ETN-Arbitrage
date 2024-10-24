from decimal import Decimal
from pandas import to_datetime
from backend.utils import get_data_type, get_snapshot, get_close


class Frame:
    def __init__(self, api=None, snapshot_init=False, code=None, category=None):
        # common attributes
        self.api = api
        self.code = code
        self.data_type = None
        self.category = category
        self.is_snapshot = None
        self.timestamp = None

        # None for snapshot
        self.simtrade = None

        # tick attributes
        self.price = None
        self.volume = None

        # bidask attributes
        self.best_bid = None
        self.best_ask = None

        # future option attributes
        self.underlying_price = None  # none for snapshot

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
            self.update_frame(snapshot)
            # self.update_close()
        
        # if code is not None and category is not None:
            # self.update_close()

    def __iter__(self):
        yield 'code', self.code
        yield 'data_type', self.data_type
        yield 'category', self.category
        yield 'is_snapshot', self.is_snapshot
        yield 'timestamp', self.timestamp
        yield 'simtrade', self.simtrade
        yield 'price', self.price
        yield 'volume', self.volume
        yield 'best_bid', self.best_bid
        yield 'best_ask', self.best_ask
        yield 'underlying_price', self.underlying_price
        yield 'close', self.close
        yield 'price_pct_chg', self.price_pct_chg
        yield 'bid_pct_chg', self.bid_pct_chg
        yield 'ask_pct_chg', self.ask_pct_chg


    def update_frame(self, data):
        self.code = data.code
        data_type, category = get_data_type(data)
        self.data_type = data_type
        self.category = category
        if category == 'fop' and data_type != 'snapshot':
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
        if data_type == 'snapshot':
            self._snapshot_to_frame(data)
        self.update_pct_chg()

    def _snapshot_to_frame(self, snapshot):
        if round(Decimal(snapshot.close), 2) != Decimal('0'):
            self.price = round(Decimal(snapshot.close), 2)
        # self.price = round(Decimal(snapshot.close), 2)
        self.timestamp = to_datetime(snapshot.ts)
        self.volume = snapshot.volume
        self.update_pct_chg()

    def _tick_to_frame(self, tick):
        self.timestamp = tick.datetime
        self.simtrade = tick.simtrade
        if tick.close != Decimal('0'):
            self.price = tick.close
        else:
            self.is_snapshot = True
        self.volume = tick.volume
        self.update_pct_chg()

    def _bidask_to_frame(self, bidask):
        self.timestamp = bidask.datetime
        self.simtrade = bidask.simtrade
        self.best_bid = bidask.bid_price[0]
        self.best_ask = bidask.ask_price[0]
        self.update_pct_chg()

    def _quote_to_frame(self, quote):
        self.timestamp = quote.datetime
        self.simtrade = quote.simtrade
        if quote.close != Decimal('0'):
            self.price = quote.close
        else:
            self.is_snapshot = True
        self.best_bid = quote.bid_price[0]
        self.best_ask = quote.ask_price[0]
        self.update_pct_chg

    def update_pct_chg(self):
        self.price_pct_chg = None
        self.bid_pct_chg = None
        self.ask_pct_chg = None
        if self.close is not None and self.close != Decimal('0'):
            if self.price is not None and self.price != Decimal('0'):
                self.price_pct_chg = round((self.price - self.close) / self.close * 100, 2)
            if self.best_bid is not None and self.best_bid != Decimal('0'):
                self.bid_pct_chg = round((self.best_bid - self.close) / self.close * 100, 2)
            if self.best_ask is not None and self.best_ask != Decimal('0'):
                self.ask_pct_chg = round((self.best_ask - self.close) / self.close * 100, 2)

    def __update_close(self):
        close = get_close(self.api, self.code, self.category, sync=True)
        self.close = round(Decimal(close), 2)
        self.update_pct_chg()
