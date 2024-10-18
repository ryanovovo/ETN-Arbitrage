import asyncio
from collections import defaultdict
from inspect import iscoroutinefunction
import subprocess


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
        self.callbacks[code][category][data_type].remove(callback)

    def clear_callbacks(self, code: str, category: str, data_type: str):
        self.callbacks[code][category][data_type].clear()

    def clear_all_callbacks(self):
        self.callbacks.clear()

    def add_callback(self,
                     code: str,
                     category: str,
                     data_type: str,
                     callback,
                     *args,
                     **kwargs):
        callback_args = {
            'args': args,
            'kwargs': kwargs
        }
        self.callbacks[code][category][data_type].append((callback, callback_args))

    def run_callbacks(self,
                      code: str,
                      category: str,
                      data_type: str,
                      data_manager):
        for callback_data in self.callbacks[code][category][data_type]:
            callback = callback_data[0]
            args = callback_data[1]['args']
            kwargs = callback_data[1]['kwargs']
            if iscoroutinefunction(callback):
                self.loop.create_task(callback(self.api, data_manager, args, kwargs))
            else:
                try:
                    self.loop.run_in_executor(None,callback, self.api,
                                              data_manager, args, kwargs)
                except KeyboardInterrupt:
                    subprocess.run(["redis-cli", "shutdown"], check=True)
                    self.loop.stop()
