from decimal import Decimal
class Arbitrage:
    def __init__(self, threshold=Decimal('0.5'), stock_frame=None, future_frame=None):
        self.stock_frame = stock_frame
        self.future_frame = future_frame
        self.bid_premium_pct = None
        self.ask_discount_pct = None
        self.price_pod_pct = None
        self.arbitrage = False
        self.expected_price = None
        self.threshold = threshold
        self.action = None
        self.action_price = None
        if stock_frame is not None and future_frame is not None:
            self.calculate_arbitrage()
    
    def set_stock_frame(self, stock_frame):
        self.stock_frame = stock_frame
    
    def set_future_frame(self, future_frame):
        self.future_frame = future_frame

    def calculate_arbitrage(self):
        if self.stock_frame.bid_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.bid_premium_pct = self.stock_frame.bid_pct_chg - self.future_frame.price_pct_chg
            if self.bid_premium_pct >= self.threshold:
                self.arbitrage = True
                self.action = 'sell'
                self.action_price = self.stock_frame.best_bid
        else:
            self.bid_premium_pct = None
        
        if self.stock_frame.ask_pct_chg is not None and self.future_frame.price_pct_chg is not None:
            self.ask_discount_pct = self.stock_frame.ask_pct_chg - self.future_frame.price_pct_chg
            if self.ask_discount_pct <= -self.threshold:
                self.arbitrage = True
                self.action = 'buy'
                self.action_price = self.stock_frame.best_ask
        else:
            self.ask_discount_pct = None
    
        self.price_pod_pct = self.stock_frame.price_pct_chg - self.future_frame.price_pct_chg
        self.expected_price = round((1 + self.future_frame.price_pct_chg * Decimal('0.01')) * self.stock_frame.close, 2)

        if self.stock_frame.simtrade:
            if self.price_pod_pct >= self.threshold:
                self.arbitrage = True
                self.action = 'sell'
                self.action_price = self.stock_frame.price
            elif self.price_pod_pct <= -self.threshold:
                self.arbitrage = True
                self.action = 'buy'
                self.action_price = self.stock_frame.price
