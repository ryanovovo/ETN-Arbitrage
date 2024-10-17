from pprint import pprint
from backend.utils import get_nearmonth_future_code
from frontend.message import arbitrage_to_embed


def callback_etn(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    stock_data = data_manager.get_latest_data('020039', 'stk', 'quote')
    future_data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'tick')

    state = kwargs['state']
    state.update_frame(stock_data)
    state.update_frame(future_data)
    stock_frame = state.get_frame('020039', 'stk')
    future_frame = state.get_frame(nearmonth_future_code, 'fop')

    webhook_manager = kwargs['webhook_manager']
    arbitrage = kwargs['arbitrage']
    arbitrage.set_stock_frame(stock_frame)
    arbitrage.set_future_frame(future_frame)
    arbitrage.calculate_arbitrage()
    webhook_manager.send_embed_message(arbitrage)
    # pprint(dict(stock_frame), sort_dicts=False)


def callback_tx_tick(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    stock_data = data_manager.get_latest_data('020039', 'stk', 'quote')
    future_data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'tick')

    state = kwargs['state']
    stock_frame = state.get_frame('020039', 'stk')
    future_frame = state.get_frame(nearmonth_future_code, 'fop')
    state.update_frame(stock_data)
    state.update_frame(future_data)
    stock_frame = state.get_frame('020039', 'stk')
    future_frame = state.get_frame(nearmonth_future_code, 'fop')
    
    webhook_manager = kwargs['webhook_manager']
    arbitrage = kwargs['arbitrage']
    arbitrage.set_stock_frame(stock_frame)
    arbitrage.set_future_frame(future_frame)
    arbitrage.calculate_arbitrage()
    webhook_manager.send_embed_message(arbitrage)
    # pprint(dict(future_frame), sort_dicts=False)

def callback_tx_bidask(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    stock_data = data_manager.get_latest_data('020039', 'stk', 'quote')
    future_data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'bidask')

    state = kwargs['state']
    state.update_frame(stock_data)
    state.update_frame(future_data)
    stock_frame = state.get_frame('020039', 'stk')
    future_frame = state.get_frame(nearmonth_future_code, 'fop')
    
    webhook_manager = kwargs['webhook_manager']
    arbitrage = kwargs['arbitrage']
    arbitrage.set_stock_frame(stock_frame)
    arbitrage.set_future_frame(future_frame)
    arbitrage.calculate_arbitrage()
    webhook_manager.send_embed_message(arbitrage)
    # print(future_data)
    # pprint(dict(future_frame), sort_dicts=False)
