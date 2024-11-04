from decimal import Decimal
from pandas import to_datetime
from backend.utils import get_data_type, get_snapshot
from datetime import datetime, timedelta
import pytz


class Frame:
    def __init__(self, api=None, snapshot_init=False, code=None, category=None):
        # common attributes
        self.api = api
        self.code = code
        self.quantity = Decimal('16')
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
        self.bid_price = [None] * 5
        self.ask_price = [None] * 5
        self.bid_volume = [None] * 5
        self.ask_volume = [None] * 5

        # future option attributes
        self.underlying_price = None  # none for snapshot

        # Other attributes
        self.close = None
        self.price_pct_chg = None
        self.bid_pct_chg = [None] * 5
        self.ask_pct_chg = [None] * 5

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
        yield 'bid_price', self.bid_price
        yield 'ask_price', self.ask_price
        yield 'bid_volume', self.bid_volume
        yield 'ask_volume', self.ask_volume
        yield 'underlying_price', self.underlying_price
        yield 'close', self.close
        yield 'price_pct_chg', round(self.price_pct_chg, 2) if self.price_pct_chg is not None else None
        yield 'bid_pct_chg', [round(value, 2) if value is not None else None for value in self.bid_pct_chg]
        yield 'ask_pct_chg', [round(value, 2) if value is not None else None for value in self.ask_pct_chg]


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
        now = datetime.now(pytz.timezone('Asia/Taipei'))
        self.timestamp = to_datetime(snapshot.ts)
        self.timestamp = self.timestamp.tz_localize('Asia/Taipei')
        if now - self.timestamp > timedelta(hours=12):
            self.price = None
            self.volume = None
            self.is_snapshot = False
            return
        if round(Decimal(snapshot.close), 2) != Decimal('0'):
            self.price = round(Decimal(snapshot.close), 2)
        if round(Decimal(snapshot.volume), 0) != Decimal('0'):
            self.volume = round(Decimal(snapshot.volume), 0)
        if round(Decimal(snapshot.buy_price), 2) != Decimal('0'):
            self.bid_price[0] = round(Decimal(snapshot.buy_price), 2)
        if round(Decimal(snapshot.sell_price), 2) != Decimal('0'):
            self.ask_price[0] = round(Decimal(snapshot.sell_price), 2)
        if round(Decimal(snapshot.buy_volume), 0) != Decimal('0'):
            self.bid_volume[0] = round(Decimal(snapshot.buy_volume), 0)
        if round(Decimal(snapshot.sell_volume), 0) != Decimal('0'):
            self.ask_volume[0] = round(Decimal(snapshot.sell_volume), 0)
        self.update_pct_chg()

    def _tick_to_frame(self, tick):
        self.timestamp = tick.datetime
        self.simtrade = tick.simtrade
        if tick.close != Decimal('0'):
            self.price = tick.close
        else:
            self.price = None
        self.volume = tick.volume
        self.update_pct_chg()

    def _bidask_to_frame(self, bidask):
        self.timestamp = bidask.datetime
        self.simtrade = bidask.simtrade
        self.bid_price = bidask.bid_price
        self.ask_price = bidask.ask_price
        self.bid_volume = bidask.bid_volume
        self.ask_volume = bidask.ask_volume
        self.update_pct_chg()

    def _quote_to_frame(self, quote):
        self.timestamp = quote.datetime
        self.simtrade = quote.simtrade
        if quote.close != Decimal('0'):
            self.price = quote.close
        else:
            self.price = None
        self.bid_price = quote.bid_price
        self.ask_price = quote.ask_price
        self.bid_volume = quote.bid_volume
        self.ask_volume = quote.ask_volume
        self.volume = quote.volume
        self.update_pct_chg()

    def update_pct_chg(self):
        self.price_pct_chg = None
        self.bid_pct_chg = [None] * 5
        self.ask_pct_chg = [None] * 5
        if self.close is not None and self.close != Decimal('0'):
            if self.price is not None and self.price != Decimal('0'):
                self.price_pct_chg = (self.price - self.close) / self.close * 100
            else:
                self.price_pct_chg = None
            for i in range(5):
                if self.bid_price[i] is not None and self.bid_price[i] != Decimal('0'):
                    self.bid_pct_chg[i] = (self.bid_price[i] - self.close) / self.close * 100
                else:
                    self.bid_pct_chg[i] = None
                if self.ask_price[i] is not None and self.ask_price[i] != Decimal('0'):
                    self.ask_pct_chg[i] = (self.ask_price[i] - self.close) / self.close * 100
                else:
                    self.ask_pct_chg[i] = None
        else:
            self.price_pct_chg = None
            self.bid_pct_chg = [None] * 5
            self.ask_pct_chg = [None] * 5
