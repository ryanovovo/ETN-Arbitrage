import logging
import os
from datetime import datetime, timedelta, time
import pytz
import pandas as pd
import shioaji as sj
from dotenv import load_dotenv
from shioaji.backend.solace.tick import TickSTKv1, TickFOPv1
from shioaji.backend.solace.bidask import BidAskSTKv1, BidAskFOPv1
from shioaji.backend.solace.quote import QuoteSTKv1
from shioaji.data import Snapshot
import json
import asyncio


def get_api():
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    SINOTRADE_API_KEY = os.getenv("SINOTRADE_API_KEY")
    SINOTRADE_SECRET_KEY = os.getenv("SINOTRADE_SECRET_KEY")
    api = sj.Shioaji(simulation=True)
    api.login(
        api_key=SINOTRADE_API_KEY,
        secret_key=SINOTRADE_SECRET_KEY,
    )
    return api


def get_snapshot(api, code: str, category: str):
    logging.warning(f"Fetching snapshot data for {category} {code}")
    if category == 'stk':
        contract = api.Contracts.Stocks[code]
    elif category == 'fop':
        contract = api.Contracts.Futures[code]
    else:
        raise ValueError(f"Invalid category: {category}")

    snapshot = api.snapshots([contract])[0]
    return snapshot


def get_nearmonth_future_code(api, code: str):
    contract = api.Contracts.Futures[code]
    if contract is None:
        raise ValueError(f"Invalid future code: {code}")
    return contract.target_code if contract.target_code != "" else code


def get_data_type(data):
    if isinstance(data, TickSTKv1):
        return 'tick', 'stk'
    if isinstance(data, TickFOPv1):
        return 'tick', 'fop'
    if isinstance(data, BidAskSTKv1):
        return 'bidask', 'stk'
    if isinstance(data, BidAskFOPv1):
        return 'bidask', 'fop'
    if isinstance(data, QuoteSTKv1):
        return 'quote', 'stk'
    if isinstance(data, Snapshot):
        if data['exchange'] == 'TSE':
            return 'snapshot', 'stk'
        elif data['exchange'] == 'TAIFEX':
            return 'snapshot', 'fop'
        else:
            raise ValueError(f"Invalid exchange: {data['exchange']}")
    raise ValueError(f"Invalid data type: {data}")


def get_nearest_fullday_kbar(api, code: str, category: str, max_try_days: int = 10):
    taipei_tz = pytz.timezone('Asia/Taipei')
    stock_market_close = time(13, 30)
    future_market_close = time(13, 45)
    contract = None
    if category == 'stk':
        contract = api.Contracts.Stocks[code]
    elif category == 'fop':
        code = code[:3]
        code += 'R1'  # for continuous contract
        contract = api.Contracts.Futures[code]
    now = datetime.now(taipei_tz)
    for i in range(max_try_days):
        date = now - timedelta(days=i)
        if date == now and date.time() <= stock_market_close and category == 'stk':
            continue
        if date == now and date.time() <= future_market_close and category == 'fop':
            continue
        date_str = date.strftime('%Y-%m-%d')
        kbars = api.kbars(contract, start=date_str, end=date_str)
        logging.info(f"Fetching kbars for {category} {code} on {date_str}")
        kbars_df = pd.DataFrame({**kbars})
        if kbars_df.empty:
            continue
        kbars_df.ts = pd.to_datetime(kbars_df.ts)
        filtered_kbars_df = kbars_df.loc[:kbars_df[kbars_df['Volume'] > 0].index[-1]]
        if not filtered_kbars_df.empty:
            return filtered_kbars_df
    raise ValueError(f"Failed to fetch kbars for {category} {code}")

def get_day_kbars(api, code, category, date):
    contract = None
    if category == 'stk':
        contract = api.Contracts.Stocks[code]
    elif category == 'fop':
        contract = api.Contracts.Futures[code]
    date_str = date.strftime('%Y-%m-%d')
    kbars = api.kbars(contract, start=date_str, end=date_str)
    logging.info(f"Fetching kbars for {category} {code} on {date_str}")
    kbars_df = pd.DataFrame({**kbars})
    if kbars_df.empty:
        raise ValueError(f"Failed to fetch kbars for {category} {code} on {date_str}")
    kbars_df.ts = pd.to_datetime(kbars_df.ts)
    return kbars_df


def get_close(api, code, category, sync=False):
    # stock_market_close = time(13, 30)
    # future_market_close = time(13, 45)
    kbars = get_nearest_fullday_kbar(api, code, category)
    logging.info(f"Fetching close price for {category} {code}")
    # timestamp = kbars.ts.iloc[-1]
    if category == 'stk' or sync:
        close = kbars.Close.iloc[-1]
    elif category == 'fop':
        close = kbars.Close.iloc[-1]
    else:
        raise ValueError(f"Invalid category: {category}")
    return close

def get_sync_future_stock_close(api, stock_code, future_code):
    stock_df = get_nearest_fullday_kbar(api, stock_code, 'stk')
    stock_close = stock_df.Close.iloc[-1]
    stock_timestamp = stock_df.ts.iloc[-1]
    future_df = get_day_kbars(api, future_code, 'fop', stock_timestamp)
    future_close = future_df[future_df.ts <= stock_timestamp].Close.iloc[-1]
    return stock_close, future_close

async def periodic_get_close(state, hours=12):
    while True:
        await asyncio.sleep(hours * 3600)
        logging.info(f"Updated close price for stock and future")
        state.update_close()


