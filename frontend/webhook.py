import requests
import os
import dotenv
import logging
from threading import RLock
from frontend.message import arbitrage_to_embed
class WebhookManager:
    def __init__(self):
        dotenv.load_dotenv()
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.last_sent_message = None
        self.lock = RLock()
        if self.webhook_url is None:
            raise ValueError("WEBHOOK_URL is required")

    def send_embed_message(self, arbitrage):
        embed = arbitrage_to_embed(arbitrage)
        embed_dict = embed.to_dict()
        data_message = {
            'embeds': [embed_dict]
        }
        headers = {
            "Content-Type": "application/json"
        }
        with self.lock:
            if not self.need_send(arbitrage):
                return True, None
            self.last_sent_message = arbitrage
        response = requests.post(self.webhook_url, json=data_message, headers=headers)
        if response.status_code != 204:
            logging.error(f"Failed to send message: {response.text}")
            return False, response.text

        return True, None
    
    def need_send(self, arbitrage):
        if self.last_sent_message is None:
            return True
        if arbitrage.action != self.last_sent_message.action and arbitrage.action != None:
            return True
        if arbitrage.action_price != self.last_sent_message.action_price and arbitrage.action_price != None:
            return True
        return False
