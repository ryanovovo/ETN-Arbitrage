import asyncio
import logging
from backend.quote import QuoteManager
from backend.utils import get_api, get_nearmonth_future_code
from backend.frame import Frame
from backend.state import State
from backend.callback_functions import callback_tx_tick, callback_tx_bidask, callback_etn

logging.basicConfig(filename='./logs/shioaji.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')
api = get_api()
print(api.usage())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
quote_manager = QuoteManager(api, loop)
nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')

etn_frame = Frame(api, snapshot_init=True, code='020039', category='stk')
etn_frame.update_close()
future_frame = Frame(api, snapshot_init=True, code=nearmonth_future_code, category='fop')
future_frame.update_close()
state = State()
state.add_frame(etn_frame)
state.add_frame(future_frame)

quote_manager.subscribe(nearmonth_future_code, 'fop', 'tick')
quote_manager.subscribe(nearmonth_future_code, 'fop', 'bidask')
quote_manager.add_callback(nearmonth_future_code, 'fop', 'tick', callback_tx_tick, state=state)
quote_manager.add_callback(nearmonth_future_code, 'fop', 'bidask', callback_tx_bidask, state=state)
quote_manager.subscribe('020039', 'stk', 'quote')
quote_manager.add_callback('020039', 'stk', 'quote', callback_etn, state=state)
loop.run_forever()
