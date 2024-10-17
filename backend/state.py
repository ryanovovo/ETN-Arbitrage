from collections import defaultdict
from backend.frame import Frame
from backend.utils import get_data_type
from backend.arbitrage import Arbitrage


class State:
    def __init__(self):
        self.frames = self.callbacks = defaultdict(lambda: {
            'stk': Frame,
            'fop': Frame
        })

    def add_frame(self, frame):
        code = frame.code
        category = frame.category
        self.frames[code][category] = frame

    def remove_frame(self, code, category):
        self.frames[code][category] = None

    def get_frame(self, code, category):
        if self.frames[code][category] is None:
            raise ValueError(f"Frame for {code} {category} is None")
        return self.frames[code][category]

    def update_frame(self, data):
        _, category = get_data_type(data)
        code = data.code
        self.frames[code][category].update_frame(data)
    
    def get_arbitrage(self, stock_code, future_code):
        stock_frame = self.get_frame(stock_code, 'stk')
        future_frame = self.get_frame(future_code, 'fop')
        arbitrage = Arbitrage(stock_frame=stock_frame, future_frame=future_frame)
        return arbitrage

        
