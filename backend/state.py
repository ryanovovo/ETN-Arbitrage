from decimal import Decimal
from backend.frame import Frame
from backend.utils import get_data_type, get_sync_future_stock_close


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
        self.expeced_profit = None
        self.fee = Decimal('0.001425')
        self.fee_discount = Decimal('0.2')
        self.tax = Decimal('0.001')
        self.stock_frame = Frame(api, snapshot_init=True, code=stock_code, category='stk')
        self.future_frame = Frame(api, snapshot_init=True, code=future_code, category='fop')
        self.update_close()

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
    
    def calculate_arbitrage(self):
        if self.stock_frame.bid_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.bid_premium_pct = self.stock_frame.bid_pct_chg - self.future_frame.price_pct_chg
            if self.bid_premium_pct >= self.threshold:
                self.arbitrage = True
                self.action = 'sell'
                self.action_price = self.stock_frame.best_bid
                pre_fee_profit = (self.action_price - self.expected_price) * 1000 * self.stock_frame.volume
                total_fee = (self.action_price * (self.fee * self.fee_discount + self.tax) + \
                            self.expected_price * (self.fee * self.fee_discount)) * \
                            1000 * self.stock_frame.volume
                self.expeced_profit = pre_fee_profit - total_fee
        else:
            self.bid_premium_pct = None
        
        if self.stock_frame.ask_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.ask_discount_pct = self.stock_frame.ask_pct_chg - self.future_frame.price_pct_chg
            if self.ask_discount_pct <= -self.threshold:
                self.arbitrage = True
                self.action = 'buy'
                self.action_price = self.stock_frame.best_ask
                pre_fee_profit = (self.expected_price - self.action_price) * 1000 * self.stock_frame.volume
                total_fee = (self.action_price * (self.fee * self.fee_discount) + \
                            self.expected_price * (self.fee * self.fee_discount + self.tax)) * \
                            1000 * self.stock_frame.volume
                self.expeced_profit = pre_fee_profit - total_fee
        else:
            self.ask_discount_pct = None
    
        self.price_pod_pct = self.stock_frame.price_pct_chg - self.future_frame.price_pct_chg
        self.expected_price = round((1 + self.future_frame.price_pct_chg * Decimal('0.01')) * self.stock_frame.close, 2)

        if self.stock_frame.simtrade:
            if self.price_pod_pct >= self.threshold:
                self.arbitrage = True
                self.action = 'sell'
                self.action_price = self.stock_frame.price
                pre_fee_profit = (self.action_price - self.expected_price) * 1000 * self.stock_frame.volume
                total_fee = (self.action_price * (self.fee * self.fee_discount + self.tax) + \
                            self.expected_price * (self.fee * self.fee_discount)) * \
                            1000 * self.stock_frame.volume
                self.expeced_profit = pre_fee_profit - total_fee
            elif self.price_pod_pct <= -self.threshold:
                self.arbitrage = True
                self.action = 'buy'
                self.action_price = self.stock_frame.price
                pre_fee_profit = (self.expected_price - self.action_price) * 1000 * self.stock_frame.volume
                total_fee = (self.action_price * (self.fee * self.fee_discount) + \
                            self.expected_price * (self.fee * self.fee_discount + self.tax)) * \
                            1000 * self.stock_frame.volume
                self.expeced_profit = pre_fee_profit - total_fee
        if self.expeced_profit is not None:
            self.expeced_profit = round(self.expeced_profit, 2)

        
