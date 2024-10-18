from collections import deque, defaultdict
from typing import Optional
from backend.utils import get_snapshot
from backend.utils import get_data_type
from threading import RLock

class DataManager:
    def __init__(self, api, max_data_size=100):
        self.api = api
        self.max_data_size = max_data_size
        self.lock = RLock()
        self.storage = defaultdict(lambda: {
            'stk': {
                'tick': deque(maxlen=max_data_size),
                'bidask': deque(maxlen=max_data_size),
                'quote': deque(maxlen=max_data_size),
                'snapshot': deque(maxlen=max_data_size),
            },
            'fop': {
                'tick': deque(maxlen=max_data_size),
                'bidask': deque(maxlen=max_data_size),
                'snapshot': deque(maxlen=max_data_size),
            }
        })
        self.subscribed = {
            'stk': {
                'tick': set(),
                'bidask': set(),
                'quote': set(),
            },
            'fop': {
                'tick': set(),
                'bidask': set(),
            }
        }

    def subscribe(self, code: str, category: str, data_type: str):
        if self.__is_subscribed(code, category, data_type):
            return
        self.subscribed[category][data_type].add(code)
        self.storage[code][category]['snapshot'].append(
            get_snapshot(self.api, code, category)
        )

    def unsubscribe(self, code: str, category: str, data_type: str):
        if not self.__is_subscribed(code, category, data_type):
            return
        self.subscribed[category][data_type].remove(code)
        self.storage[code][category][data_type].clear()

    def add_data(self, data):
        data_type, category = get_data_type(data)
        code = data.code
        self.__add_data(code, category, data_type, data)

    def get_data(self, code: str,
                 category: str,
                 data_type: str,
                 size: Optional[int] = None):

        data = list(self.storage[code][category][data_type])
        if size > self.max_data_size:
            raise ValueError(
                f"Size {size} exceeds maximum size {self.max_data_size}"
            )
        if not self.__is_empty(code, category, data_type):
            raise ValueError(
                f"Code {code} has no {category} {data_type} data"
            )
        if size > len(data):
            raise ValueError(
                f"Size {size} exceeds available data size "
                f"{len(data)}"
            )

        if size is not None:
            return data[-size:]
        return data

    def get_latest_data(self, code: str,
                        category: str,
                        data_type: str,
                        snapshot: bool = True):
        if self.__is_empty(code, category, data_type):
            if snapshot:
                return self.storage[code][category]['snapshot'][-1]
            raise ValueError(
                f"Code {code} has no {category} {data_type} data"
            )
        return self.storage[code][category][data_type][-1]

    def __is_subscribed(self, code: str, category: str, data_type: str):
        return code in self.subscribed[category][data_type]

    def __add_data(self, code: str, category: str, data_type: str, data):
        if not self.__is_subscribed(code, category, data_type):
            raise ValueError(
                f"Code {code} is not subscribed to {category} {data_type}"
            )
        self.storage[code][category][data_type].append(data)

    def __is_empty(self, code: str, category: str, data_type: str):
        with self.lock:
            return code not in self.subscribed[category][data_type] or \
                len(self.storage[code][category][data_type]) == 0
