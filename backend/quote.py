import asyncio
from backend.callback import CallbackManager
from backend.data_redis import DataManager
import logging


class QuoteManager:
    def __init__(self,
                 api,
                 loop: asyncio.AbstractEventLoop,
                 max_tasks=100,
                 max_data_size=100):
        self.api = api
        self.loop = loop
        self.callback_manager = CallbackManager(api, loop, max_tasks)
        self.data_manager = DataManager(api, max_data_size)
        self.api.quote.set_on_tick_stk_v1_callback(
            self.on_data_received('stk', 'tick')
        )
        self.api.quote.set_on_tick_fop_v1_callback(
            self.on_data_received('fop', 'tick')
        )
        self.api.quote.set_on_bidask_stk_v1_callback(
            self.on_data_received('stk', 'bidask')
        )
        self.api.quote.set_on_bidask_fop_v1_callback(
            self.on_data_received('fop', 'bidask')
        )
        self.api.quote.set_on_quote_stk_v1_callback(
            self.on_data_received('stk', 'quote')
        )

    def __del__(self):
        self.clear_all_callbacks()

    def on_data_received(self, category: str, data_type: str):
        def handler(_exchange, data):
            self.data_manager.add_data(data)
            self.callback_manager.run_callbacks(data.code, category, data_type, data)
        return handler

    def subscribe(self, code: str, category: str, data_type: str):
        if category == 'stk':
            contract = self.api.Contracts.Stocks[code]
        elif category == 'fop':
            # code = get_nearmonth_future_code(self.api, code)
            contract = self.api.Contracts.Futures[code]
        else:
            raise ValueError(f"Invalid category: {category}")
        self.api.quote.subscribe(contract, data_type)
        self.data_manager.subscribe(code, category, data_type)
        logging.info(f"Subscribed to {category} {data_type} {code}")

    def unsubscribe(self, code: str, category: str, data_type: str):
        if category == 'stk':
            contract = self.api.Contracts.Stocks[code]
        elif category == 'fop':
            # code = get_nearmonth_future_code(self.api, code)
            contract = self.api.Contracts.Futures[code]
        else:
            raise ValueError(f"Invalid category: {category}")
        self.api.quote.unsubscribe(contract, data_type)
        self.data_manager.unsubscribe(code, category, data_type)
        logging.info(f"Unsubscribed from {category} {data_type} {code}")

    def add_callback(self,code: str, category: str, data_type: str,
                     callback, *args, **kwargs):
        self.callback_manager.add_callback(code, category, data_type,
                                           callback, *args, **kwargs)

    def clear_callbacks(self, code: str, category: str, data_type: str):
        self.callback_manager.clear_callbacks(code, category, data_type)

    def clear_all_callbacks(self):
        self.callback_manager.clear_all_callbacks()
