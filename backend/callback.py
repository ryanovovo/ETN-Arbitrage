import asyncio
from collections import defaultdict
from inspect import iscoroutinefunction
import subprocess
from backend.utils import get_nearmonth_future_code


class CallbackManager:
    def __init__(self, api, loop: asyncio.AbstractEventLoop, max_tasks=100):
        self.api = api
        self.loop = loop
        self.max_tasks = max_tasks
        self.callbacks = defaultdict(lambda: {
            'stk': {
                    'tick': [],
                    'bidask': [],
                    'quote': []
                },
            'fop': {
                    'tick': [],
                    'bidask': []
                }
            }
        )
        self.tasks = defaultdict(lambda: {
            'stk': {
                    'tick': [],
                    'bidask': [],
                    'quote': []
                },
            'fop': {
                    'tick': [],
                    'bidask': []
                }
            }
        )

    def remove_callback(self, code: str,
                        category: str,
                        data_type: str,
                        callback):
        if category == 'fop':
            nearmonth_future_code = get_nearmonth_future_code(self.api, code)
            if nearmonth_future_code == code:
                code = code[:3] + 'R1'
        self.callbacks[code][category][data_type].remove(callback)

    def clear_callbacks(self, code: str, category: str, data_type: str):
        if category == 'fop':
            nearmonth_future_code = get_nearmonth_future_code(self.api, code)
            if nearmonth_future_code == code:
                code = code[:3] + 'R1'
        self.callbacks[code][category][data_type].clear()

    def clear_all_callbacks(self):
        self.callbacks.clear()

    def add_callback(self, code: str, category: str, data_type: str,
                     callback, *args, **kwargs):
        if category == 'fop':
            nearmonth_future_code = get_nearmonth_future_code(self.api, code)
            if nearmonth_future_code == code:
                code = code[:3] + 'R1'
        callback_args = {
            'args': args,
            'kwargs': kwargs
        }
        self.callbacks[code][category][data_type].append((callback, callback_args))

    def run_callbacks(self, code: str, category: str, data_type: str, data):
        if category == 'fop':
            nearmonth_future_code = get_nearmonth_future_code(self.api, code)
            if nearmonth_future_code == code:
                code = code[:3] + 'R1'
        for callback_data in self.callbacks[code][category][data_type]:
            callback = callback_data[0]
            args = callback_data[1]['args']
            kwargs = callback_data[1]['kwargs']
            if iscoroutinefunction(callback):
                self.loop.create_task(callback(data, args, kwargs))
            else:
                self.loop.run_in_executor(None, callback, data, args, kwargs)
