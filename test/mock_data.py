from shioaji.backend.solace.tick import TickSTKv1, TickFOPv1
from shioaji.backend.solace.bidask import BidAskSTKv1, BidAskFOPv1
from shioaji.backend.solace.quote import QuoteSTKv1
from shioaji.data import Snapshot
from decimal import Decimal
import datetime
from backend.state import State

stk_tick = TickSTKv1(
    code = '2330', 
    datetime = datetime.datetime(2021, 7, 2, 13, 16, 35, 92970), 
    open = Decimal('590'), 
    avg_price = Decimal('589.05'), 
    close = Decimal('590'), 
    high = Decimal('593'), 
    low = Decimal('587'), 
    amount = Decimal('590000'), 
    total_amount = Decimal('8540101000'), 
    volume = 1, 
    total_volume = 14498, 
    tick_type = 1, 
    chg_type = 4, 
    price_chg = Decimal('-3'), 
    pct_chg = Decimal('-0.505902'), 
    bid_side_total_vol= 6638, 
    ask_side_total_vol = 7860, 
    bid_side_total_cnt = 2694, 
    ask_side_total_cnt = 2705, 
    closing_oddlot_shares = 0, 
    fixed_trade_vol = 0, 
    suspend = 0, 
    simtrade = 1,
    intraday_odd = 0
)

stk_bidask = BidAskSTKv1(
    code = '2330',
    datetime = datetime.datetime(2021, 7, 2, 13, 17, 45, 743299),
    bid_price = [Decimal('589'), Decimal('588'), Decimal('587'), Decimal('586'), Decimal('585')], 
    bid_volume = [59391, 224490, 74082, 68570, 125246], 
    diff_bid_vol = [49874, 101808, 23863, 38712, 77704], 
    ask_price = [Decimal('590'), Decimal('591'), Decimal('592'), Decimal('593'), Decimal('594')], 
    ask_volume = [26355, 9680, 18087, 11773, 3568], 
    diff_ask_vol = [13251, -14347, 39249, -20397, -10591], 
    suspend = 0, 
    simtrade = 1, 
    intraday_odd = 1
)

stk_quote = QuoteSTKv1(
    code='2330', 
    datetime=datetime.datetime(2022, 7, 1, 10, 43, 15, 430329), 
    open=Decimal('471.5'), 
    avg_price=Decimal('467.91'), 
    close=Decimal('461'), 
    high=Decimal('474'), 
    low=Decimal('461'), 
    amount=Decimal('461000'), 
    total_amount=Decimal('11834476000'), 
    volume=1, 
    total_volume=25292, 
    tick_type=2, 
    chg_type=4, 
    price_chg=Decimal('-15'), 
    pct_chg=Decimal('-3.15'), 
    bid_side_total_vol=9350, 
    ask_side_total_vol=15942, 
    bid_side_total_cnt=2730, 
    ask_side_total_cnt=2847, 
    closing_oddlot_shares=0, 
    closing_oddlot_close=Decimal('0.0'), 
    closing_oddlot_amount=Decimal('0'), 
    closing_oddlot_bid_price=Decimal('0.0'), 
    closing_oddlot_ask_price=Decimal('0.0'), 
    fixed_trade_vol=0, 
    fixed_trade_amount=Decimal('0'), 
    bid_price=[Decimal('461'), Decimal('460.5'), Decimal('460'), Decimal('459.5'), Decimal('459')], 
    bid_volume=[220, 140, 994, 63, 132], 
    diff_bid_vol=[-1, 0, 0, 0, 0], 
    ask_price=[Decimal('461.5'), Decimal('462'), Decimal('462.5'), Decimal('463'), Decimal('463.5')], 
    ask_volume=[115, 101, 103, 147, 91], 
    diff_ask_vol=[0, 0, 0, 0, 0], 
    avail_borrowing=9579699, 
    suspend=0, 
    simtrade=1
)

fop_tick = TickFOPv1(
    code = 'TXFG1', 
    datetime = datetime.datetime(2021, 7, 1, 10, 42, 29, 757000), 
    open = Decimal('17678'), 
    underlying_price = Decimal('17849.57'), 
    bid_side_total_vol= 32210, 
    ask_side_total_vol= 33218, 
    avg_price = Decimal('17704.663999'), 
    close = Decimal('17753'), 
    high = Decimal('17774'), 
    low = Decimal('17655'), 
    amount = Decimal('17753'), 
    total_amount = Decimal('913790823'), 
    volume = 1, 
    total_volume = 51613, 
    tick_type = 0, 
    chg_type = 2, 
    price_chg = Decimal('41'), 
    pct_chg = Decimal('0.231481'), 
    simtrade = 1
)



fop_bidask = BidAskFOPv1(
    code = 'TXFG1', 
    datetime = datetime.datetime(2021, 7, 1, 10, 51, 31, 999000), 
    bid_total_vol = 66, 
    ask_total_vol = 101, 
    bid_price = [Decimal('17746'), Decimal('17745'), Decimal('17744'), Decimal('17743'), Decimal('17742')], 
    bid_volume = [1, 14, 19, 17, 15], 
    diff_bid_vol = [0, 1, 0, 0, 0], 
    ask_price = [Decimal('17747'), Decimal('17748'), Decimal('17749'), Decimal('17750'), Decimal('17751')], 
    ask_volume = [6, 22, 25, 32, 16], 
    diff_ask_vol = [0, 0, 0, 0, 0], 
    first_derived_bid_price = Decimal('17743'), 
    first_derived_ask_price = Decimal('17751'), 
    first_derived_bid_vol = 1, 
    first_derived_ask_vol = 1, 
    underlying_price = Decimal('17827.94'), 
    simtrade = 1
)



