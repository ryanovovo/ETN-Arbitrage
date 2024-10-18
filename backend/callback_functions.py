from backend.utils import get_nearmonth_future_code


def callback_update(data, args, kwargs):
    try:
        state = kwargs['state']
    except KeyError:
        raise ValueError("State is required")
    state.update_frame(data)
    webhook_manager = kwargs.get('webhook_manager')
    if webhook_manager is not None:
        webhook_manager.send_embed_message(state)
    # pprint(dict(future_frame), sort_dicts=False)
