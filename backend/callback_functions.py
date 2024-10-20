import threading

state_lock = threading.RLock()


def callback_update(data, args, kwargs):
    updated_state = None
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
    # pprint(dict(future_frame), sort_dicts=False)
