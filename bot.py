# Import necessary libraries and modules
import asyncio
import logging
from decimal import Decimal
from backend.quote import QuoteManager
from backend.utils import get_api, periodic_get_close
from backend.frame import Frame
from backend.state import State
from backend.callback_functions import callback_update
from frontend.webhook import WebhookManager
from frontend.message import state_to_embed
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import os
from dotenv import load_dotenv
import signal
from datetime import datetime, timedelta
import pytz

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

stock_code = '020039'
future_code = 'TXFR1'
# future_code = get_nearmonth_future_code(api, future_code)

state = State(api, stock_code=stock_code, future_code=future_code)
webhook_manager = WebhookManager()

# Subscribe and set callback functions
quote_manager.subscribe(future_code, 'fop', 'tick')
quote_manager.subscribe(future_code, 'fop', 'bidask')
quote_manager.subscribe(stock_code, 'stk', 'tick')
quote_manager.subscribe(stock_code, 'stk', 'bidask')
quote_manager.add_callback(future_code, 'fop', 'tick', callback_update, state=state, webhook_manager=webhook_manager)
quote_manager.add_callback(future_code, 'fop', 'bidask', callback_update, state=state, webhook_manager=webhook_manager)
quote_manager.add_callback(stock_code, 'stk', 'tick', callback_update, state=state, webhook_manager=webhook_manager)
quote_manager.add_callback(stock_code, 'stk', 'bidask', callback_update, state=state, webhook_manager=webhook_manager)

# Initialize Discord bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Global variables to store messages
last_message = None
last_stream_message = None
is_subscribed = True
streaming = False

class StatusView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="API狀態", style=discord.ButtonStyle.primary)
    async def bot_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        global last_message

        # Get API usage information
        usage = api.usage()
        used_mib = round(Decimal(usage['bytes']) / 1024 / 1024, 2)
        remaining_mib = round(Decimal(usage['remaining_bytes']) / 1024 / 1024, 2)
        used_pct = round(usage['bytes'] / usage['limit_bytes'] * 100, 2)
        unused_pct = round(Decimal(100 - used_pct), 2)
        
        # Create an embed message
        if unused_pct >= 50:
            color = discord.Color.green()
        elif unused_pct >= 20:
            color = discord.Color.orange()
        else:
            color = discord.Color.red()
        embed = discord.Embed(title="API使用量", color=color)
        embed.add_field(name='已使用比例', value=str(used_pct)+'%', inline=False)
        embed.add_field(name='剩餘比例', value=str(unused_pct)+'%', inline=True)
        embed.add_field(name='已使用流量', value=f"{used_mib} MiB", inline=True)
        embed.add_field(name='剩餘流量', value=f"{remaining_mib} MiB", inline=True)
        if is_subscribed:
            embed.add_field(name='訂閱狀態', value="已訂閱", inline=False)
        else:
            embed.add_field(name='訂閱狀態', value="未訂閱", inline=False)
        if streaming:
            embed.add_field(name='串流狀態', value="已啟用", inline=False)
        else:
            embed.add_field(name='串流狀態', value="已停止", inline=False)
        embed.add_field(name='收盤價更新時間', value=state.updated_close_timestamp.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

        # Edit the last sent message
        if last_message:
            await last_message.edit(embed=embed, view=self)
        await interaction.response.defer()

    @discord.ui.button(label="取消訂閱", style=discord.ButtonStyle.danger)
    async def unsubscribe_market(self, interaction: discord.Interaction, button: discord.ui.Button):
        global last_message
        global is_subscribed
        if is_subscribed:
            quote_manager.unsubscribe(future_code, 'fop', 'tick')
            quote_manager.unsubscribe(future_code, 'fop', 'bidask')
            quote_manager.unsubscribe(stock_code, 'stk', 'quote')
            embed = discord.Embed(title="已取消訂閱！", color=0xFF0000)
            if last_message:
                await last_message.edit(embed=embed, view=self)
            await interaction.response.defer()
            is_subscribed = False
        else:
            embed = discord.Embed(title="已取消訂閱！", color=0xFF0000)
            if last_message:
                await last_message.edit(embed=embed, view=self)
            await interaction.response.defer()

    @discord.ui.button(label="套利資訊", style=discord.ButtonStyle.success)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        global is_subscribed
        if not is_subscribed:
            quote_manager.subscribe(future_code, 'fop', 'tick')
            quote_manager.subscribe(future_code, 'fop', 'bidask')
            quote_manager.subscribe(stock_code, 'stk', 'quote')
            is_subscribed = True
        # 傳送嵌入式套利資訊訊息，編輯上一次發送的訊息
        now = datetime.now(pytz.timezone('Asia/Taipei'))
        if now - state.updated_close_timestamp > timedelta(hours=6):
            state.update_close()
        embed = state_to_embed(state)

        global last_message
        if last_message:
            # 編輯之前發送的訊息
            await last_message.edit(embed=embed, view=self)
        await interaction.response.defer()

class StreamView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="開始串流", style=discord.ButtonStyle.success)
    async def start_stream(self, interaction: discord.Interaction, button: discord.ui.Button):
        global streaming
        if not streaming:
            streaming = True
            self.stream_embed.start()
        await interaction.response.defer()

    @discord.ui.button(label="結束串流", style=discord.ButtonStyle.danger)
    async def stop_stream(self, interaction: discord.Interaction, button: discord.ui.Button):
        global streaming, last_stream_message
        if streaming:
            streaming = False
            self.stream_embed.stop()
            if last_stream_message:
                stop_embed = discord.Embed(title="已停止串流", color=0xFF0000)
                await last_stream_message.edit(embed=stop_embed, view=self)
        await interaction.response.defer()

    @tasks.loop(seconds=5)
    async def stream_embed(self):
        global last_stream_message
        if streaming:
            stream_embed = state_to_embed(state)
            if last_stream_message:
                await last_stream_message.edit(embed=stream_embed, view=self)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # Specify the channel to send messages
    global channel_id, stream_channel_id
    webhook_channel_id = int(os.getenv('WEBHOOK_CHANNEL_ID'))
    stream_channel_id = int(os.getenv('STREAM_CHANNEL_ID'))
    bot_channel = bot.get_channel(channel_id)
    stream_channel = bot.get_channel(stream_channel_id)
    webhook_channel = bot.get_channel(webhook_channel_id)
    
    if bot_channel:
        await bot_channel.purge(limit=100)  # Clear messages on startup
        status_view = StatusView()
        global last_message
        # Send initial button message and save it for subsequent editing
        last_message = await bot_channel.send(view=status_view)
    else:
        print(f"Channel with ID {channel_id} not found.")
        logging.error(f"Channel with ID {channel_id} not found.")
    
    if stream_channel:
        await stream_channel.purge(limit=100)  # Clear messages on startup
        stream_view = StreamView()
        global last_stream_message
        # Send initial stream message and save it for subsequent editing
        last_stream_message = await stream_channel.send(view=stream_view)
    else:
        print(f"Channel with ID {stream_channel_id} not found.")
        logging.error(f"Channel with ID {stream_channel_id} not found.")
    
    if webhook_channel:
        webhook_last_message = [message async for message in webhook_channel.history(limit=1)]
        if webhook_last_message:
            webhook_last_message_id = webhook_last_message[0].id
            await webhook_channel.purge(limit=100, check=lambda msg: msg.id != webhook_last_message_id)
    else:
        print(f"Channel with ID {webhook_channel_id} not found.")
        logging.error(f"Channel with ID {webhook_channel_id} not found.")

# Get channel and bot token
load_dotenv()
channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
bot_token = os.getenv('DISCORD_BOT_TOKEN')

# Run the bot and bind it to the event loop
loop.create_task(bot.start(bot_token))
loop.create_task(periodic_get_close(state, hours=12))
loop.run_forever()
