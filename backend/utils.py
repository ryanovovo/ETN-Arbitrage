import logging
import shioaji as sj
import os
from dotenv import load_dotenv


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
