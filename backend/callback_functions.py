import threading
from pprint import pprint
import copy

state_lock = threading.RLock()


def callback_update(data, args, kwargs):
    with state_lock:
        try:
            state = kwargs['state']
        except KeyError:
            raise ValueError("State is required")
        state.update_frame(data)
        updated_state_dict = dict(state)
    webhook_manager = kwargs.get('webhook_manager')
    if webhook_manager is not None:
        webhook_manager.send_embed_message(updated_state_dict)
    # pprint(dict(state.stock_frame), sort_dicts=False)

def callback_update_terminal(data, args, kwargs):
    with state_lock:
        try:
            state = kwargs['state']
        except KeyError:
            raise ValueError("State is required")
        state.update_frame(data)
        updated_state_dict = dict(state)
        console_manager = kwargs.get('console_manager')
        if console_manager is not None:
            console_manager.state_to_terminal(updated_state_dict)
