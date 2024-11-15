from decimal import Decimal
from datetime import datetime
from backend.frame import Frame
from backend.utils import get_data_type, get_sync_future_stock_close
import pytz


class State:
    def __init__(self, api, stock_code, future_code):
        self.api = api
        self.balance = Decimal('100000')
        self.stock_frame = None
        self.future_frame = None
        self.bid_premium_pct = [None] * 5
        self.ask_discount_pct = [None] * 5
        self.price_pod_pct = None
        self.arbitrage = False
        self.expected_price = None
        self.threshold = Decimal('0.6')
        self.action = None
        self.action_price = None
        self.expected_profit = None
        self.bid_expected_profit = [None] * 5
        self.ask_expected_profit = [None] * 5
        self.price_sell_expected_profit = None
        self.price_buy_expected_profit = None
        self.fee = Decimal('0.001425')
        self.fee_discount = Decimal('0.2')
        self.tax = Decimal('0.001')
        self.slippage = Decimal('0.03')
        self.stock_frame = Frame(api, snapshot_init=True, code=stock_code, category='stk')
        self.future_frame = Frame(api, snapshot_init=True, code=future_code, category='fop')
        self.updated_close_timestamp = None
        self.update_close()
    
    def __iter__(self):
        yield 'balance', self.balance
        yield 'stock_frame', dict(self.stock_frame)
        yield 'future_frame', dict(self.future_frame)
        yield 'bid_premium_pct', [round(value, 2) if value is not None else None for value in self.bid_premium_pct]
        yield 'ask_discount_pct', [round(value, 2) if value is not None else None for value in self.ask_discount_pct]
        yield 'price_pod_pct', round(self.price_pod_pct, 2) if self.price_pod_pct is not None else None
        yield 'arbitrage', self.arbitrage
        yield 'expected_price', self.expected_price
        yield 'threshold', self.threshold
        yield 'action', self.action
        yield 'action_price', self.action_price
        yield 'expected_profit', round(self.expected_profit, 2) if self.expected_profit is not None else None
        yield 'bid_expected_profit', [round(value, 2) if value is not None else None for value in self.bid_expected_profit]
        yield 'ask_expected_profit', [round(value, 2) if value is not None else None for value in self.ask_expected_profit]
        yield 'price_sell_expected_profit', round(self.price_sell_expected_profit, 2) if self.price_sell_expected_profit is not None else None
        yield 'price_buy_expected_profit', round(self.price_buy_expected_profit, 2) if self.price_buy_expected_profit is not None else None
        yield 'fee', self.fee
        yield 'fee_discount', self.fee_discount
        yield 'tax', self.tax
        yield 'slippage', self.slippage
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
        self.bid_expected_profit = [None] * 5
        self.ask_expected_profit = [None] * 5
        self.bid_premium_pct = [None] * 5
        self.ask_discount_pct = [None] * 5
        self.price_buy_expected_profit = None
        self.price_sell_expected_profit = None
        self.arbitrage = False
        if self.stock_frame.close is not None and self.future_frame.price_pct_chg is not None:
            self.expected_price = round((1 + self.future_frame.price_pct_chg * Decimal('0.01')) * self.stock_frame.close, 3)

        for i in range(5):
            if self.stock_frame.bid_pct_chg[i] is not None and self.future_frame.price_pct_chg is not None:
                self.bid_premium_pct[i] = self.stock_frame.bid_pct_chg[i] - self.future_frame.price_pct_chg
                if self.stock_frame.bid_price[i] is not None and self.stock_frame.bid_volume[i] is not None:
                    max_sell_volume = min(sum(self.stock_frame.bid_volume[:i+1]), self.stock_frame.quantity)
                    pre_fee_profit = (self.stock_frame.bid_price[i] - self.expected_price) * 1000 * max_sell_volume
                    total_fee = (self.stock_frame.bid_price[i] * (self.fee * self.fee_discount + self.tax) + \
                                self.expected_price * (self.fee * self.fee_discount)) * \
                                1000 * max_sell_volume
                    self.bid_expected_profit[i] = pre_fee_profit - total_fee
                else:
                    self.bid_expected_profit[i] = None
            else:
                self.bid_premium_pct[i] = None
                self.bid_expected_profit[i] = None
        
        for i in range(5):
            if self.stock_frame.ask_pct_chg[i] is not None and self.future_frame.price_pct_chg is not None:
                self.ask_discount_pct[i] = self.stock_frame.ask_pct_chg[i] - self.future_frame.price_pct_chg
                # if self.ask_discount_pct[i] <= -self.threshold:
            
                if self.stock_frame.ask_price[i] is not None and self.stock_frame.ask_volume[i] is not None:
                    max_buy_volume = min(sum(self.stock_frame.ask_volume[:i+1]), self.balance // (self.stock_frame.ask_price[i] * 1000))
                    pre_fee_profit = (self.expected_price - self.stock_frame.ask_price[i]) * 1000 * max_buy_volume
                    total_fee = (self.stock_frame.ask_price[i] * (self.fee * self.fee_discount) +
                                self.expected_price * (self.fee * self.fee_discount + self.tax)) * \
                                1000 * max_buy_volume
                    self.ask_expected_profit[i] = pre_fee_profit - total_fee
                else:
                    self.ask_expected_profit[i] = None
            else:
                self.ask_discount_pct[i] = None
                self.ask_expected_profit[i] = None


        if self.stock_frame.price_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.price_pod_pct = self.stock_frame.price_pct_chg - self.future_frame.price_pct_chg
            max_sell_volume = min(self.stock_frame.quantity, self.stock_frame.volume)
            max_buy_volume = min(self.balance // (self.stock_frame.price * 1000), self.stock_frame.volume)
            pre_fee_sell_profit = (self.stock_frame.price - self.expected_price - self.slippage) * 1000 * max_sell_volume
            pre_fee_buy_profit = (self.expected_price - self.stock_frame.price - self.slippage) * 1000 * max_buy_volume
            sell_total_fee = (self.stock_frame.price * (self.fee * self.fee_discount + self.tax) + \
                        self.expected_price * (self.fee * self.fee_discount)) * 1000 * max_sell_volume
            buy_total_fee = (self.stock_frame.price * (self.fee * self.fee_discount) + \
                        self.expected_price * (self.fee * self.fee_discount + self.tax)) * 1000 * max_buy_volume
            self.price_sell_expected_profit = pre_fee_sell_profit - sell_total_fee
            self.price_buy_expected_profit = pre_fee_buy_profit - buy_total_fee
        else:
            self.price_pod_pct = None
            self.price_sell_expected_profit = None
            self.price_buy_expected_profit = None

        max_profit = Decimal('0')
        for i in range(5):
            if self.bid_expected_profit[i] is not None and self.bid_expected_profit[i] > max_profit \
                and self.bid_premium_pct[i] >= self.threshold:

                max_profit = self.bid_expected_profit[i]
                self.action = 'sell'
                self.action_price = self.stock_frame.bid_price[i]
                self.expected_profit = self.bid_expected_profit[i]
            if self.ask_expected_profit[i] is not None and self.ask_expected_profit[i] > max_profit \
                and self.ask_discount_pct[i] <= -self.threshold:

                max_profit = self.ask_expected_profit[i]
                self.action = 'buy'
                self.action_price = self.stock_frame.ask_price[i]
                self.expected_profit = self.ask_expected_profit[i]

        if self.price_sell_expected_profit is not None and self.price_sell_expected_profit > max_profit \
            and self.price_pod_pct >= self.threshold and self.stock_frame.simtrade:

            max_profit = self.price_sell_expected_profit
            self.action = 'sell'
            self.action_price = self.stock_frame.price - self.slippage
            self.expected_profit = self.price_sell_expected_profit
        elif self.price_buy_expected_profit is not None and self.price_buy_expected_profit > max_profit \
                and self.price_pod_pct <= -self.threshold and self.stock_frame.simtrade:
            
            max_profit = self.price_buy_expected_profit
            self.action = 'buy'
            self.action_price = self.stock_frame.price + self.slippage
            self.expected_profit = self.price_buy_expected_profit

        
