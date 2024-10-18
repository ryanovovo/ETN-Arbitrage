import requests
import os
import dotenv
import logging
from threading import RLock
from frontend.message import state_to_embed
class WebhookManager:
    def __init__(self):
        dotenv.load_dotenv()
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.last_sent_state = None
        self.lock = RLock()
        if self.webhook_url is None:
            raise ValueError("WEBHOOK_URL is required")

    def send_embed_message(self, state):
        embed = state_to_embed(state)
        embed_dict = embed.to_dict()
        data_message = {
            'embeds': [embed_dict]
        }
        headers = {
            "Content-Type": "application/json"
        }
        with self.lock:
            if not self.need_send(state):
                return True, None
            self.last_sent_state = state
        response = requests.post(self.webhook_url, json=data_message, headers=headers)
        if response.status_code != 204:
            logging.error(f"Failed to send message: {response.text}")
            return False, response.text

        return True, None
    
    def need_send(self, state):
        if self.last_sent_state is None:
            return True
        if state.action != self.last_sent_state.action and state.action != None:
            return True
        if state.action_price != self.last_sent_state.action_price and state.action_price != None:
            return True
        if state.expected_price != self.last_sent_state.expected_price and state.expected_price != None:
            return True
        # For debugging
        return False
