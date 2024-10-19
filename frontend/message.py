import discord
def state_to_embed(state):
    if state.action == 'sell':
        color = discord.Color.green()
    elif state.action == 'buy':
        color = discord.Color.red()
    else:
        color = discord.Color.dark_gray()
    stock_frame = state.stock_frame
    future_frame = state.future_frame
    if stock_frame.simtrade:
        stock_mark = ' [試搓] ' 
    if stock_frame.is_snapshot:
        stock_mark = ' [快照] '
    else:
        stock_mark = ' '

    if future_frame.simtrade:
        future_mark = ' [試搓] '
    if future_frame.is_snapshot:
        future_mark = ' [快照] '
    else:
        future_mark = ' '

    if state.action == 'sell':
        action = '賣出'
    elif state.action == 'buy':
        action = '買進'
    else:
        action = '無'
    embed = discord.Embed(title='市場資訊', color=color)

    # embed.add_field(name='-'*40, value='', inline=False)
    # embed.add_field(name='台灣加權指數', value=str(future_frame.underlying_price), inline=False)
    embed.add_field(name='-'*40, value='', inline=False)

    embed.add_field(name='台指期資訊', value='', inline=False)
    embed.add_field(name=future_frame.timestamp.strftime("%Y-%m-%d %H:%M:%S"), value='', inline=True)
    embed.add_field(name='最新成交價', value=f"{str(future_frame.price)}{future_mark}({str(future_frame.price_pct_chg)}%)", inline=False)
    embed.add_field(name='台指期現貨同步收盤價', value=str(future_frame.close), inline=True)
    embed.add_field(name='-'*40, value='', inline=False)

    embed.add_field(name='ETN資訊', value='', inline=False)
    embed.add_field(name=stock_frame.timestamp.strftime("%Y-%m-%d %H:%M:%S"), value='', inline=True)
    embed.add_field(name='成交價', value=f"{str(stock_frame.price)}{stock_mark}({str(stock_frame.price_pct_chg)}%)", inline=True)
    embed.add_field(name='成交量', value=str(stock_frame.volume), inline=False)
    embed.add_field(name='最佳買價', value=f"{str(stock_frame.best_bid)} ({str(stock_frame.bid_pct_chg)}%)", inline=True)
    embed.add_field(name='最佳賣價', value=f"{str(stock_frame.best_ask)} ({str(stock_frame.ask_pct_chg)}%)", inline=True)
    embed.add_field(name='預期價格', value=str(state.expected_price), inline=False)
    embed.add_field(name='-'*40, value='', inline=False)

    embed.add_field(name='套利機會', value='', inline=False)
    embed.add_field(name='買賣方向', value=action, inline=False) 
    embed.add_field(name='執行價格', value=str(state.action_price), inline=False)
    embed.add_field(name='預期利潤', value=str(state.expeced_profit), inline=False)
    embed.add_field(name='-'*40, value='', inline=False)
    return embed