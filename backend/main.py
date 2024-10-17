from quote import QuoteManager
from utils import get_api, get_nearmonth_future_code
import asyncio
from time import sleep
import logging
from pprint import pprint


def callback_2330(args, kwargs):
    data_manager = kwargs['_data_manager']
    data = data_manager.get_latest_data('2330', 'stk', 'tick')
    data = dict(data)
    pprint(data, sort_dicts=False)

def callback_tx(args, kwargs):
    data_manager = kwargs['_data_manager']
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'tick')
    data = dict(data)
    pprint(data, sort_dicts=False)
    print("kwargs", kwargs)
    sleep(10) # simulate long running task


logging.basicConfig(filename='./logs/shioaji.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')
api = get_api()
print(api.usage())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
quote_manager = QuoteManager(api, loop)
nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
quote_manager.subscribe(nearmonth_future_code, 'fop', 'tick')
quote_manager.add_callback(nearmonth_future_code, 'fop', 'tick', callback_tx, message='hello')
# quote_manager.subscribe('2330', 'stk', 'tick')
# quote_manager.add_callback('2330', 'stk', 'tick', callback_2330)
loop.run_forever()
