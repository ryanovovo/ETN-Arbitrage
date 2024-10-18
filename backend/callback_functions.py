from pprint import pprint
from backend.utils import get_nearmonth_future_code
from frontend.message import state_to_embed
import json

def update(kwargs, stock_data, future_data):
    state = kwargs['state']
    state.update_frame(stock_data)
    state.update_frame(future_data)

    webhook_manager = kwargs['webhook_manager']
    webhook_manager.send_embed_message(state)
    # pprint(dict(future_frame), sort_dicts=False)


def callback_etn(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    stock_data = data_manager.get_latest_data('020039', 'stk', 'quote')
    future_data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'tick')
    update(kwargs, stock_data, future_data)
    # pprint(dict(stock_frame), sort_dicts=False)


def callback_tx_tick(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    stock_data = data_manager.get_latest_data('020039', 'stk', 'quote')
    future_data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'tick')
    update(kwargs, stock_data, future_data)


def callback_tx_bidask(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    stock_data = data_manager.get_latest_data('020039', 'stk', 'quote')
    future_data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'bidask')
    future_frame = kwargs['state'].future_frame
    update(kwargs, stock_data, future_data)
    pprint(json.dumps(future_data.to_dict(raw=True)), sort_dicts=False)
