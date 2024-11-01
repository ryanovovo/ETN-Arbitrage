from decimal import Decimal
from datetime import datetime
from backend.frame import Frame
from backend.utils import get_data_type, get_sync_future_stock_close
import pytz


class State:
    def __init__(self, api, stock_code, future_code):
        self.api = api
        self.stock_frame = None
        self.future_frame = None
        self.bid_premium_pct = None
        self.ask_discount_pct = None
        self.price_pod_pct = None
        self.arbitrage = False
        self.expected_price = None
        self.threshold = Decimal('0.5')
        self.action = None
        self.action_price = None
        self.expected_profit = None
        self.fee = Decimal('0.001425')
        self.fee_discount = Decimal('0.2')
        self.tax = Decimal('0.001')
        self.stock_frame = Frame(api, snapshot_init=True, code=stock_code, category='stk')
        self.future_frame = Frame(api, snapshot_init=True, code=future_code, category='fop')
        self.updated_close_timestamp = None
        self.update_close()
    
    def __iter__(self):
        yield 'stock_frame', dict(self.stock_frame)
        yield 'future_frame', dict(self.future_frame)
        yield 'bid_premium_pct', self.bid_premium_pct
        yield 'ask_discount_pct', self.ask_discount_pct
        yield 'price_pod_pct', self.price_pod_pct
        yield 'arbitrage', self.arbitrage
        yield 'expected_price', self.expected_price
        yield 'threshold', self.threshold
        yield 'action', self.action
        yield 'action_price', self.action_price
        yield 'expected_profit', self.expected_profit
        yield 'fee', self.fee
        yield 'fee_discount', self.fee_discount
        yield 'tax', self.tax
        yield 'updated_close_timestamp', self.updated_close_timestamp

    def get_frame(self, category):
        if category == 'stk':
            return self.stock_frame
        elif category == 'fop':
            return self.future_frame
        else:
            raise ValueError(f"Invalid category: {category}")

    def update_frame(self, data):
        _, category = get_data_type(data)
        if category == 'stk':
            self.stock_frame.update_frame(data)
        elif category == 'fop':
            self.future_frame.update_frame(data)
        else:
            raise ValueError(f"Invalid category: {category}")
        self.calculate_arbitrage()
    
    def update_close(self):
        stock_close, future_close = get_sync_future_stock_close(self.api, self.stock_frame.code, self.future_frame.code)
        self.stock_frame.close = round(Decimal(stock_close), 2)
        self.future_frame.close = round(Decimal(future_close), 2)
        self.stock_frame.update_pct_chg()
        self.future_frame.update_pct_chg()
        self.calculate_arbitrage()
        self.updated_close_timestamp = datetime.now(pytz.timezone('Asia/Taipei'))
    
    def calculate_arbitrage(self):
        self.action = None
        self.action_price = None
        self.expected_profit = None
        self.arbitrage = False
        if self.stock_frame.bid_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.bid_premium_pct = self.stock_frame.bid_pct_chg - self.future_frame.price_pct_chg
            if self.bid_premium_pct >= self.threshold:
                self.arbitrage = True
                self.action = 'sell'
                self.action_price = self.stock_frame.best_bid
                if self.stock_frame.volume is not None:
                    pre_fee_profit = (self.action_price - self.expected_price) * 1000 * self.stock_frame.volume
                    total_fee = (self.action_price * (self.fee * self.fee_discount + self.tax) + \
                                self.expected_price * (self.fee * self.fee_discount)) * \
                                1000 * self.stock_frame.volume
                    self.expected_profit = pre_fee_profit - total_fee
                else:
                    self.expected_profit = None
        else:
            self.bid_premium_pct = None
        
        if self.stock_frame.ask_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.ask_discount_pct = self.stock_frame.ask_pct_chg - self.future_frame.price_pct_chg
            if self.ask_discount_pct <= -self.threshold:
                self.arbitrage = True
                self.action = 'buy'
                self.action_price = self.stock_frame.best_ask
                if self.stock_frame.volume is not None:
                    pre_fee_profit = (self.expected_price - self.action_price) * 1000 * self.stock_frame.volume
                    total_fee = (self.action_price * (self.fee * self.fee_discount) + \
                                self.expected_price * (self.fee * self.fee_discount + self.tax)) * \
                                1000 * self.stock_frame.volume
                    self.expected_profit = pre_fee_profit - total_fee
                else:
                    self.expected_profit = None
        else:
            self.ask_discount_pct = None

        if self.stock_frame.close is not None and self.future_frame.price_pct_chg is not None:
            self.expected_price = round((1 + self.future_frame.price_pct_chg * Decimal('0.01')) * self.stock_frame.close, 3)

        if self.stock_frame.price_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.price_pod_pct = self.stock_frame.price_pct_chg - self.future_frame.price_pct_chg

            if self.stock_frame.simtrade:
                if self.price_pod_pct >= self.threshold:
                    self.arbitrage = True
                    self.action = 'sell'
                    self.action_price = self.stock_frame.price
                    if self.stock_frame.volume is not None:
                        pre_fee_profit = (self.action_price - self.expected_price) * 1000 * self.stock_frame.volume
                        total_fee = (self.action_price * (self.fee * self.fee_discount + self.tax) + \
                                    self.expected_price * (self.fee * self.fee_discount)) * \
                                    1000 * self.stock_frame.volume
                        self.expected_profit = pre_fee_profit - total_fee
                    else:
                        self.expected_profit = None
                elif self.price_pod_pct <= -self.threshold:
                    self.arbitrage = True
                    self.action = 'buy'
                    self.action_price = self.stock_frame.price
                    if self.stock_frame.volume is not None:
                        pre_fee_profit = (self.expected_price - self.action_price) * 1000 * self.stock_frame.volume
                        total_fee = (self.action_price * (self.fee * self.fee_discount) + \
                                    self.expected_price * (self.fee * self.fee_discount + self.tax)) * \
                                    1000 * self.stock_frame.volume
                        self.expected_profit = pre_fee_profit - total_fee
                    else:
                        self.expected_profit = None
        if self.expected_profit is not None:
            self.expected_profit = round(self.expected_profit, 2)

        
