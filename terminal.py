# Import necessary libraries and modules
import asyncio
import logging
from backend.quote import QuoteManager
from backend.utils import get_api, periodic_get_close
from backend.state import State
from backend.callback_functions import callback_update_terminal
from frontend.console import ConsoleManager
import signal

# Set up logging
logging.basicConfig(filename='./logs/shioaji.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

# Initialize API and data
api = get_api()
print(api.usage())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.add_signal_handler(signal.SIGINT, loop.stop)
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

quote_manager = QuoteManager(api, loop)
console_manager = ConsoleManager()

stock_code = '020039'
future_code = 'TXFR1'
# future_code = get_nearmonth_future_code(api, future_code)

state = State(api, stock_code=stock_code, future_code=future_code)
console_manager.state_to_debug(dict(state))

# Subscribe and set callback functions
quote_manager.subscribe(future_code, 'fop', 'tick')
quote_manager.subscribe(future_code, 'fop', 'bidask')
quote_manager.subscribe(stock_code, 'stk', 'tick')
quote_manager.subscribe(stock_code, 'stk', 'bidask')
quote_manager.add_callback(future_code, 'fop', 'tick', callback_update_terminal, state=state, console_manager=console_manager)
quote_manager.add_callback(future_code, 'fop', 'bidask', callback_update_terminal, state=state, console_manager=console_manager)
quote_manager.add_callback(stock_code, 'stk', 'tick', callback_update_terminal, state=state, console_manager=console_manager)
quote_manager.add_callback(stock_code, 'stk', 'bidask', callback_update_terminal, state=state, console_manager=console_manager)


loop.create_task(periodic_get_close(state, hours=12))
loop.run_forever()
