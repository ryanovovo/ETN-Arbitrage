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
from discord.ext import commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv
import signal

# 設定日誌
logging.basicConfig(filename='./logs/shioaji.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

# 初始化API及資料
api = get_api()
print(api.usage())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
quote_manager = QuoteManager(api, loop)

stock_code = '020039'
future_code = 'TXFR1'
# future_code = get_nearmonth_future_code(api, future_code)

state = State(api, stock_code=stock_code, future_code=future_code)
webhook_manager = WebhookManager()

# 訂閱與回調設定
quote_manager.subscribe(future_code, 'fop', 'tick')
quote_manager.subscribe(future_code, 'fop', 'bidask')
quote_manager.subscribe(stock_code, 'stk', 'quote')
quote_manager.add_callback(future_code, 'fop', 'tick', callback_update, state=state, webhook_manager=webhook_manager)
quote_manager.add_callback(future_code, 'fop', 'bidask', callback_update, state=state, webhook_manager=webhook_manager)
quote_manager.add_callback(stock_code, 'stk', 'quote', callback_update, state=state, webhook_manager=webhook_manager)

# 初始化Discord機器人
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# 全局變量，存儲發送的訊息
last_message = None
is_subscribed = True

class MyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="API狀態", style=discord.ButtonStyle.primary)
    async def bot_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 顯示API使用狀況（類似於 usage 函數的回傳值）
        global last_message

        # 獲取 API 的使用資訊
        usage = api.usage()
        used_mib = round(Decimal(usage['bytes']) / 1024 / 1024, 2)
        remaining_mib = round(Decimal(usage['remaining_bytes']) / 1024 / 1024, 2)
        used_pct = round(usage['bytes'] / usage['limit_bytes'] * 100, 2)
        unused_pct = round(Decimal(100 - used_pct), 2)
        
        # 創建嵌入訊息
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
        embed.add_field(name='收盤價更新時間', value=state.updated_close_timestamp.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

        # 使用 edit() 編輯最後發送的訊息
        if last_message:
            await last_message.edit(content="", embed=embed, view=self)
        await interaction.response.defer()

    @discord.ui.button(label="訂閱行情", style=discord.ButtonStyle.success)
    async def subscribe_market(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 訂閱操作
        global last_message
        global is_subscribed
        if not is_subscribed:
            quote_manager.subscribe(future_code, 'fop', 'tick')
            quote_manager.subscribe(future_code, 'fop', 'bidask')
            quote_manager.subscribe(stock_code, 'stk', 'quote')
            embed = discord.Embed(title="已訂閱！", color=0x00FF00)
            if last_message:
                await last_message.edit(content="", embed=embed, view=self)
            await interaction.response.defer()
            is_subscribed = True
        else:
            embed = discord.Embed(title="已訂閱！", color=0x00FF00)
            if last_message:
                await last_message.edit(content="", embed=embed, view=self)
            await interaction.response.defer()

    @discord.ui.button(label="取消訂閱", style=discord.ButtonStyle.danger)
    async def unsubscribe_market(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 取消訂閱操作
        global last_message
        global is_subscribed
        if is_subscribed:
            quote_manager.unsubscribe(future_code, 'fop', 'tick')
            quote_manager.unsubscribe(future_code, 'fop', 'bidask')
            quote_manager.unsubscribe(stock_code, 'stk', 'quote')
            embed = discord.Embed(title="已取消訂閱！", color=0xFF0000)
            if last_message:
                await last_message.edit(content="", embed=embed, view=self)
            await interaction.response.defer()
            is_subscribed = False
        else:
            embed = discord.Embed(title="已取消訂閱！", color=0xFF0000)
            if last_message:
                await last_message.edit(content="", embed=embed, view=self)
            await interaction.response.defer()

    @discord.ui.button(label="套利資訊", style=discord.ButtonStyle.primary)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 傳送嵌入式套利資訊訊息，編輯上一次發送的訊息
        state.update_close()
        embed = state_to_embed(state)

        global last_message
        if last_message:
            # 編輯之前發送的訊息
            await last_message.edit(content="", embed=embed, view=self)
        await interaction.response.defer()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # 指定要傳送訊息的頻道 ID
    global channel_id
    webhook_channel_id = int(os.getenv('WEBHOOK_CHANNEL_ID'))
    bot_channel = bot.get_channel(channel_id)
    webhook_channel = bot.get_channel(webhook_channel_id)
    
    if bot_channel:
        await bot_channel.purge(limit=100)  # 啟動時清理訊息
        view = MyView()
        global last_message
        # 傳送初始按鈕訊息並保存該訊息以供後續編輯
        last_message = await bot_channel.send("請選擇指令:", view=view)
    else:
        print(f"Channel with ID {channel_id} not found.")
        logging.error(f"Channel with ID {channel_id} not found.")
    
    if webhook_channel:
        webhook_last_message = [message async for message in webhook_channel.history(limit=1)]
        if webhook_last_message:
            webhook_last_message_id = webhook_last_message[0].id
            await webhook_channel.purge(limit=100, check=lambda msg: msg.id != webhook_last_message_id)
    else:
        print(f"Channel with ID {webhook_channel_id} not found.")
        logging.error(f"Channel with ID {webhook_channel_id} not found.")

# 獲取頻道和機器人的 token
load_dotenv()
channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
bot_token = os.getenv('DISCORD_BOT_TOKEN')

loop.add_signal_handler(signal.SIGINT, loop.stop)
signal.signal(signal.SIGCHLD, signal.SIG_IGN)
# 啟動機器人並將其綁定到事件循環
loop.create_task(bot.start(bot_token))
loop.create_task(periodic_get_close(state, hours=12))
loop.run_forever()
