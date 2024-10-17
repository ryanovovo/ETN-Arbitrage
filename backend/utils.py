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
        date_str = date.strftime('%Y-%m-%d')
        kbars = api.kbars(contract, start=date_str, end=date_str)
        logging.info(f"Fetching kbars for {category} {code} on {date_str}")
        kbars_df = pd.DataFrame({**kbars})
        kbars_df.ts = pd.to_datetime(kbars_df.ts)
        if category == 'stk':
            if not kbars_df[kbars_df.ts.dt.time == stock_market_close].empty:
                return kbars_df
        elif category == 'fop':
            if not kbars_df[kbars_df.ts.dt.time == future_market_close].empty:
                return kbars_df
    raise ValueError(f"Failed to fetch kbars for {category} {code}")


def get_close(api, code, category, sync=False):
    stock_market_close = time(13, 30)
    future_market_close = time(13, 45)
    kbars = get_nearest_fullday_kbar(api, code, category)
    if category == 'stk' or sync:
        close = kbars[kbars.ts.dt.time == stock_market_close].Close.iloc[0]
    elif category == 'fop':
        close = kbars[kbars.ts.dt.time == future_market_close].Close.iloc[0]
    else:
        raise ValueError(f"Invalid category: {category}")
    return close
