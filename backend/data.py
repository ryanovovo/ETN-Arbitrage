from collections import deque, defaultdict
from typing import Optional
from shioaji.backend.solace.tick import TickSTKv1, TickFOPv1
from shioaji.backend.solace.bidask import BidAskSTKv1, BidAskFOPv1
from shioaji.backend.solace.quote import QuoteSTKv1
from shioaji.data import Snapshot
from utils import get_snapshot


class DataManager:
    def __init__(self, api, max_data_size=100):
        self.api = api
        self.max_data_size = max_data_size
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
            raise ValueError(
                f"Code {code} is already subscribed to {category} {data_type}"
            )
        self.subscribed[category][data_type].add(code)
        self.storage[code][category]['snapshot'].append(
            get_snapshot(self.api, code, category)
        )

    def unsubscribe(self, code: str, category: str, data_type: str):
        if not self.__is_subscribed(code, category, data_type):
            raise ValueError(
                f"Code {code} is not subscribed to {category} {data_type}"
            )
        self.subscribed[category][data_type].remove(code)
        self.storage[code][category][data_type].clear()

    def add_data(self, data):
        data_type, category = self.__get_data_type(data)
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
            else:
                raise ValueError(
                    f"Code {code} has no {category} {data_type} data"
                )
        return self.storage[code][category][data_type][-1]

    def __is_subscribed(self, code: str, category: str, data_type: str):
        return code in self.subscribed[category][data_type]

    def __get_data_type(self, data):
        if isinstance(data, TickSTKv1):
            return 'tick', 'stk'
        elif isinstance(data, TickFOPv1):
            return 'tick', 'fop'
        elif isinstance(data, BidAskSTKv1):
            return 'bidask', 'stk'
        elif isinstance(data, BidAskFOPv1):
            return 'bidask', 'fop'
        elif isinstance(data, QuoteSTKv1):
            return 'quote', 'stk'
        elif isinstance(data, Snapshot):
            if data['exchange'] == 'TSE':
                return 'snapshot', 'stk'
            elif data['exchange'] == 'TFE':
                return 'snapshot', 'fop'
            else:
                raise ValueError(f"Invalid exchange: {data['exchange']}")
        else:
            raise ValueError(f"Invalid data type: {type(data)}")

    def __add_data(self, code: str, category: str, data_type: str, data):
        if not self.__is_subscribed(code, category, data_type):
            raise ValueError(
                f"Code {code} is not subscribed to {category} {data_type}"
            )
        self.storage[code][category][data_type].append(data)

    def __is_empty(self, code: str, category: str, data_type: str):
        return code not in self.subscribed[category][data_type] and \
               len(self.storage[code][category][data_type]) == 0
