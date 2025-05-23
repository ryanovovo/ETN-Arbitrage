import requests
import os
import dotenv
import logging
from threading import RLock
from frontend.message import state_to_embed
from datetime import datetime, timedelta
import pytz
class WebhookManager:
    def __init__(self):
        dotenv.load_dotenv()
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.last_sent_state = None
        self.lock = RLock()
        if self.webhook_url is None:
            raise ValueError("WEBHOOK_URL is required")

    def send_embed_message(self, state_dict, force_send=False):
        if not isinstance(state_dict, dict):
            state_dict = dict(state_dict)
        with self.lock:
            if not self.need_send(state_dict) and not force_send:
                return True, None
            else:
                self.last_sent_state = state_dict
        embed = state_to_embed(state_dict)
        embed_dict = embed.to_dict()
        data_message = {
            'embeds': [embed_dict]
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(self.webhook_url, json=data_message, headers=headers)
        if response.status_code != 204:
            logging.error(f"Failed to send message: {response.text}")
            return False, response.text

        return True, None

    def need_send(self, state_dict):
        tz = pytz.timezone("Asia/Taipei")
        now = datetime.now(tz)

        stock_ts = state_dict['stock_frame']['timestamp']
        future_ts = state_dict['future_frame']['timestamp']

        # 強制轉為 Asia/Taipei 時區的 tz-aware
        if stock_ts.tzinfo is None:
            stock_ts = tz.localize(stock_ts)
        else:
            stock_ts = stock_ts.astimezone(tz)

        if future_ts.tzinfo is None:
            future_ts = tz.localize(future_ts)
        else:
            future_ts = future_ts.astimezone(tz)

        if now - stock_ts > timedelta(minutes=10):
            return False
        if now - future_ts > timedelta(minutes=10):
            return False 
        if self.last_sent_state is None:
            if state_dict['action'] is not None:
                return True
            return False
        if state_dict['action'] != self.last_sent_state['action']:
            return True
        if state_dict['action_price'] != self.last_sent_state['action_price'] and state_dict['action_price'] is not None:
            return True
        # if state_dict['expected_price'] != self.last_sent_state['expected_price'] and state_dict['expected_price'] is not None:
        #     return True
        # if state_dict['expected_profit'] != self.last_sent_state['expected_profit'] and state_dict['expected_profit'] is not None:
        #     return True
        return False
