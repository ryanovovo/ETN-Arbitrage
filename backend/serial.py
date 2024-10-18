from datetime import datetime
from decimal import Decimal
import json
from shioaji.backend.solace.tick import TickSTKv1, TickFOPv1
from shioaji.backend.solace.bidask import BidAskSTKv1, BidAskFOPv1
from shioaji.backend.solace.quote import QuoteSTKv1
from shioaji.constant import ChangeType, TickType
from shioaji.data import Snapshot
def dict_to_stk_tick(data_dict):
    stk_tick = TickSTKv1(
        code=data_dict['code'],
        datetime=datetime.fromisoformat(data_dict['datetime']),  # 将 ISO 8601 字符串转换为 datetime 对象
        open=Decimal(data_dict['open']),
        avg_price=Decimal(data_dict['avg_price']),
        close=Decimal(data_dict['close']),
        high=Decimal(data_dict['high']),
        low=Decimal(data_dict['low']),
        amount=Decimal(data_dict['amount']),
        total_amount=Decimal(data_dict['total_amount']),
        volume=int(data_dict['volume']),
        total_volume=int(data_dict['total_volume']),
        tick_type=int(data_dict['tick_type']),
        chg_type=int(data_dict['chg_type']),
        price_chg=Decimal(data_dict['price_chg']),
        pct_chg=Decimal(data_dict['pct_chg']),
        bid_side_total_vol=int(data_dict['bid_side_total_vol']),
        ask_side_total_vol=int(data_dict['ask_side_total_vol']),
        bid_side_total_cnt=int(data_dict['bid_side_total_cnt']),
        ask_side_total_cnt=int(data_dict['ask_side_total_cnt']),
        closing_oddlot_shares=int(data_dict['closing_oddlot_shares']),
        fixed_trade_vol=int(data_dict['fixed_trade_vol']),
        suspend=bool(data_dict['suspend'] == 'True'),  # 将字符串转换为布尔值
        simtrade=bool(data_dict['simtrade'] == 'True'),
        intraday_odd=bool(data_dict['intraday_odd'] == 'True')
    )
    return stk_tick

def dict_to_stk_bidask(data_dict):
    stk_bidask = BidAskSTKv1(
        code=data_dict['code'],
        datetime=datetime.fromisoformat(data_dict['datetime']),  # 将日期字符串转换为 datetime 对象
        bid_price=[Decimal(price) for price in data_dict['bid_price']],  # 将价格字符串转换为 Decimal 列表
        bid_volume=[int(vol) for vol in data_dict['bid_volume']],        # 将交易量字符串转换为 int 列表
        diff_bid_vol=[int(diff) for diff in data_dict['diff_bid_vol']],  # 将交易量变化字符串转换为 int 列表
        ask_price=[Decimal(price) for price in data_dict['ask_price']],  # 将价格字符串转换为 Decimal 列表
        ask_volume=[int(vol) for vol in data_dict['ask_volume']],        # 将交易量字符串转换为 int 列表
        diff_ask_vol=[int(diff) for diff in data_dict['diff_ask_vol']],  # 将交易量变化字符串转换为 int 列表
        suspend=bool(data_dict['suspend'] == 'True'),  # 字符串转换为布尔值
        simtrade=bool(data_dict['simtrade'] == 'True'), 
        intraday_odd=bool(data_dict['intraday_odd'] == 'True')
    )
    return stk_bidask


def dict_to_stk_quote(data_dict):
    stk_quote = QuoteSTKv1(
        code=data_dict['code'],
        datetime=datetime.fromisoformat(data_dict['datetime']),
        open=Decimal(data_dict['open']),
        avg_price=Decimal(data_dict['avg_price']),
        close=Decimal(data_dict['close']),
        high=Decimal(data_dict['high']),
        low=Decimal(data_dict['low']),
        amount=Decimal(data_dict['amount']),
        total_amount=Decimal(data_dict['total_amount']),
        volume=int(data_dict['volume']),
        total_volume=int(data_dict['total_volume']),
        tick_type=int(data_dict['tick_type']),
        chg_type=int(data_dict['chg_type']),
        price_chg=Decimal(data_dict['price_chg']),
        pct_chg=Decimal(data_dict['pct_chg']),
        bid_side_total_vol=int(data_dict['bid_side_total_vol']),
        ask_side_total_vol=int(data_dict['ask_side_total_vol']),
        bid_side_total_cnt=int(data_dict['bid_side_total_cnt']),
        ask_side_total_cnt=int(data_dict['ask_side_total_cnt']),
        closing_oddlot_shares=int(data_dict['closing_oddlot_shares']),
        closing_oddlot_close=Decimal(data_dict['closing_oddlot_close']),
        closing_oddlot_amount=Decimal(data_dict['closing_oddlot_amount']),
        closing_oddlot_bid_price=Decimal(data_dict['closing_oddlot_bid_price']),
        closing_oddlot_ask_price=Decimal(data_dict['closing_oddlot_ask_price']),
        fixed_trade_vol=int(data_dict['fixed_trade_vol']),
        fixed_trade_amount=Decimal(data_dict['fixed_trade_amount']),
        bid_price=[Decimal(price) for price in data_dict['bid_price']],
        bid_volume=[int(vol) for vol in data_dict['bid_volume']],
        diff_bid_vol=[int(vol) for vol in data_dict['diff_bid_vol']],
        ask_price=[Decimal(price) for price in data_dict['ask_price']],
        ask_volume=[int(vol) for vol in data_dict['ask_volume']],
        diff_ask_vol=[int(vol) for vol in data_dict['diff_ask_vol']],
        avail_borrowing=int(data_dict['avail_borrowing']),
        suspend=bool(data_dict['suspend'] == 'True'),
        simtrade=bool(data_dict['simtrade'] == 'True')
    )
    return stk_quote

def dict_to_fop_tick(data_dict):
    fop_tick = TickFOPv1(
        code=data_dict['code'],
        datetime=datetime.fromisoformat(data_dict['datetime']),  # 将日期字符串转换为 datetime 对象
        open=Decimal(data_dict['open']),                         # 将字符串转换为 Decimal
        underlying_price=Decimal(data_dict['underlying_price']), # 标的资产价格转换为 Decimal
        bid_side_total_vol=int(data_dict['bid_side_total_vol']), # 将字符串转换为 int
        ask_side_total_vol=int(data_dict['ask_side_total_vol']), # 将字符串转换为 int
        avg_price=Decimal(data_dict['avg_price']),               # 将字符串转换为 Decimal
        close=Decimal(data_dict['close']),                       # 将字符串转换为 Decimal
        high=Decimal(data_dict['high']),                         # 将字符串转换为 Decimal
        low=Decimal(data_dict['low']),                           # 将字符串转换为 Decimal
        amount=Decimal(data_dict['amount']),                     # 将字符串转换为 Decimal
        total_amount=Decimal(data_dict['total_amount']),         # 将字符串转换为 Decimal
        volume=int(data_dict['volume']),                         # 将字符串转换为 int
        total_volume=int(data_dict['total_volume']),             # 将字符串转换为 int
        tick_type=int(data_dict['tick_type']),                   # 将字符串转换为 int
        chg_type=int(data_dict['chg_type']),                     # 将字符串转换为 int
        price_chg=Decimal(data_dict['price_chg']),               # 将字符串转换为 Decimal
        pct_chg=Decimal(data_dict['pct_chg']),                   # 将字符串转换为 Decimal
        simtrade=bool(data_dict['simtrade'] == 'True')           # 将字符串转换为布尔值
    )
    return fop_tick

def dict_to_fop_bidask(data_dict):
    fop_bidask = BidAskFOPv1(
        code=data_dict['code'],
        datetime=datetime.fromisoformat(data_dict['datetime']),  # 将日期字符串转换为 datetime 对象
        bid_total_vol=int(data_dict['bid_total_vol']),           # 将字符串转换为 int
        ask_total_vol=int(data_dict['ask_total_vol']),           # 将字符串转换为 int
        bid_price=[Decimal(price) for price in data_dict['bid_price']],  # 将价格字符串列表转换为 Decimal 列表
        bid_volume=[int(vol) for vol in data_dict['bid_volume']],        # 将交易量字符串列表转换为 int 列表
        diff_bid_vol=[int(diff) for diff in data_dict['diff_bid_vol']],  # 将变化量字符串列表转换为 int 列表
        ask_price=[Decimal(price) for price in data_dict['ask_price']],  # 将价格字符串列表转换为 Decimal 列表
        ask_volume=[int(vol) for vol in data_dict['ask_volume']],        # 将交易量字符串列表转换为 int 列表
        diff_ask_vol=[int(diff) for diff in data_dict['diff_ask_vol']],  # 将变化量字符串列表转换为 int 列表
        first_derived_bid_price=Decimal(data_dict['first_derived_bid_price']),  # 将字符串转换为 Decimal
        first_derived_ask_price=Decimal(data_dict['first_derived_ask_price']),  # 将字符串转换为 Decimal
        first_derived_bid_vol=int(data_dict['first_derived_bid_vol']),   # 将字符串转换为 int
        first_derived_ask_vol=int(data_dict['first_derived_ask_vol']),   # 将字符串转换为 int
        underlying_price=Decimal(data_dict['underlying_price']),         # 将字符串转换为 Decimal
        simtrade=bool(data_dict['simtrade'] == 'True')                   # 将字符串转换为布尔值
    )
    return fop_bidask

def dict_to_snapshot(data_dict):
    snapshot = Snapshot(
        ts=data_dict['ts'],                               # 时间戳 (int)
        code=data_dict['code'],                           # 股票代码 (str)
        exchange=data_dict['exchange'],                   # 交易所 (str)
        open=data_dict['open'],                           # 开盘价 (float)
        high=data_dict['high'],                           # 最高价 (float)
        low=data_dict['low'],                             # 最低价 (float)
        close=data_dict['close'],                         # 收盘价 (float)
        tick_type=TickType[data_dict['tick_type']],       # 将字符串转换为 TickType 枚举
        change_price=data_dict['change_price'],           # 价格变动 (float)
        change_rate=data_dict['change_rate'],             # 变动率 (float)
        change_type=ChangeType[data_dict['change_type']], # 将字符串转换为 ChangeType 枚举
        average_price=data_dict['average_price'],         # 均价 (float)
        volume=data_dict['volume'],                       # 成交量 (int)
        total_volume=data_dict['total_volume'],           # 总成交量 (int)
        amount=data_dict['amount'],                       # 成交金额 (int)
        total_amount=data_dict['total_amount'],           # 总成交金额 (int)
        yesterday_volume=data_dict['yesterday_volume'],   # 昨日成交量 (float)
        buy_price=data_dict['buy_price'],                 # 买入价 (float)
        buy_volume=data_dict['buy_volume'],               # 买入量 (float)
        sell_price=data_dict['sell_price'],               # 卖出价 (float)
        sell_volume=data_dict['sell_volume'],             # 卖出量 (int)
        volume_ratio=data_dict['volume_ratio']            # 成交量比率 (float)
    )
    return snapshot

def datetime_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # 使用 ISO 格式序列化
    raise TypeError("Type not serializable")

def serialize(data, category, data_type):
    if data_type == 'snapshot':
        data_dict = dict(data)
    else:
        data_dict = data.to_dict(raw=True)
    data_dict['category'] = category
    data_dict['data_type'] = data_type
    json_data = json.dumps(data_dict, default=datetime_converter)
    return json_data

def deserialize(json_data):
    if isinstance(json_data, str):
        data_dict = json.loads(json_data)
    else:
        data_dict = json_data

    # 檢查是否有 'data' 鍵，並解析內部的 JSON 字符串
    if 'data' in data_dict:
        # 再次解析內部的 JSON 字符串
        data_dict = json.loads(data_dict['data'])
    else:
        raise KeyError("Missing 'data' key in the JSON data")

    category = data_dict['category']
    data_type = data_dict['data_type']
    if category == 'stk':
        if data_type == 'tick':
            return dict_to_stk_tick(data_dict)
        if data_type == 'bidask':
            return dict_to_stk_bidask(data_dict)
        if data_type == 'quote':
            return dict_to_stk_quote(data_dict)
    if category == 'fop':
        if data_type == 'tick':
            return dict_to_fop_tick(data_dict)
        if data_type == 'bidask':
            return dict_to_fop_bidask(data_dict)
    if data_type == 'snapshot':
        return dict_to_snapshot(data_dict)