from pprint import pprint
from backend.utils import get_nearmonth_future_code


def callback_etn(api, data_manager, args, kwargs):
    data = data_manager.get_latest_data('020039', 'stk', 'quote')
    data = dict(data)
    pprint(data, sort_dicts=False)


def callback_tx_tick(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'tick')
    state = kwargs['state']
    state.update_frame(data)
    frame = state.get_frame(nearmonth_future_code, 'fop')
    pprint(dict(frame), sort_dicts=False)


def callback_tx_bidask(api, data_manager, args, kwargs):
    nearmonth_future_code = get_nearmonth_future_code(api, 'TXFR1')
    data = data_manager.get_latest_data(nearmonth_future_code, 'fop', 'bidask')
    state = kwargs['state']
    state.update_frame(data)
    frame = state.get_frame(nearmonth_future_code, 'fop')
    pprint(dict(frame), sort_dicts=False)
