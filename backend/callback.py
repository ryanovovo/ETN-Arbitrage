import asyncio
from collections import defaultdict
from inspect import iscoroutinefunction


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


    def __is_empty(self, code: str, category: str, data_type: str):
        return code not in self.callbacks[category][data_type] and \
                len(self.callbacks[code][category][data_type]) == 0

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
        callback
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
            kwargs['_data_manager'] = data_manager
            if iscoroutinefunction(callback):
                self.loop.create_task(callback(args, kwargs))
            else:
                self.loop.run_in_executor(None, callback, args, kwargs)
