import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.callback_functions import callback_update
from mock_data import stk_tick, stk_bidask, stk_quote, fop_tick, fop_bidask
from frontend.webhook import WebhookManager
from time import sleep
from backend.state import State
from backend.utils import get_api
import asyncio



def test_callback_update():
    api = get_api()
    webhook_manager = WebhookManager()
    mock_state = State(api, stock_code='2330', future_code='TXFR1')
    kwargs = {
        'state': mock_state,
        'webhook_manager': webhook_manager
    }
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # callback_update(stk_tick, None, kwargs)
    callback_update(stk_bidask, None, kwargs)
    callback_update(stk_quote, None, kwargs)
    callback_update(fop_tick, None, kwargs)
    callback_update(fop_bidask, None, kwargs)
    for _ in range(1000):
        # loop.run_in_executor(None, callback_update, stk_tick, None, kwargs)
        loop.run_in_executor(None, callback_update, stk_bidask, None, kwargs)
        loop.run_in_executor(None, callback_update, stk_quote, None, kwargs)
        loop.run_in_executor(None, callback_update, fop_tick, None, kwargs)
        loop.run_in_executor(None, callback_update, fop_bidask, None, kwargs)


test_callback_update()
sleep(50)
