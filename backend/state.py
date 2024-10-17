from .frame import Frame
from collections import defaultdict
from .utils import get_data_type


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
        data_type, category = get_data_type(data)
        code = data.code
        self.frames[code][category].data_to_frame(data)
