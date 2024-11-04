import curses
from datetime import datetime, timedelta
from pprint import pprint

class ConsoleManager:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.curs_set(0)  # 隱藏游標
        self.last_clear = datetime.now()

        # 初始化顏色組合
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # 紅色
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 綠色

    def state_to_terminal(self, state):
        # 移動到特定位置而不是清除整個螢幕
        
        self.stdscr.move(0, 0)

        # 通過字典鍵訪問 'action' 屬性
        if not isinstance(state, dict):
            state_dict = dict(state)
        else:
            state_dict = state

        stock_frame = state_dict['stock_frame']
        future_frame = state_dict['future_frame']

        # 通過字典鍵訪問 'stock_frame' 的屬性
        stock_mark = ' [試搓] ' if stock_frame['simtrade'] else ' [快照] ' if stock_frame['is_snapshot'] else ' '

        # 通過字典鍵訪問 'future_frame' 的屬性
        future_mark = ' [試搓] ' if future_frame['simtrade'] else ' [快照] ' if future_frame['is_snapshot'] else ' '

        action = '賣出' if state_dict['action'] == 'sell' else '買進' if state_dict['action'] == 'buy' else '無'

        # 獲取當前時間
        now = datetime.now()
        if now - self.last_clear > timedelta(seconds=10.0):
            self.stdscr.clear()
            self.last_clear = now

        # 輸出資訊到終端，每次輸出後用設定好的空格來確保覆蓋舊的內容
        self.stdscr.addstr(0, 0, f"市場資訊 {now}")
        self.stdscr.addstr(1, 0, '-'*40)

        # 新增台灣加權指數顯示
        self.stdscr.addstr(2, 0, f"台灣加權指數: {future_frame['underlying_price']}")

        # 加入分隔線
        self.stdscr.addstr(3, 0, '-'*40)
        
        self.stdscr.addstr(4, 0, "台指期資訊")
        self.stdscr.addstr(5, 0, f"時間: {future_frame['timestamp']}")
        self.stdscr.addstr(6, 0, f"台指期現貨同步收盤價: {future_frame['close']}")
        self.stdscr.addstr(7, 0, f"最新成交價: {future_frame['price']}{future_mark} ({future_frame['price_pct_chg']}%)")
        self.stdscr.addstr(8, 0, '-'*40)
        self.stdscr.addstr(9, 0, "ETN資訊")
        self.stdscr.addstr(10, 0, f"時間: {stock_frame['timestamp']}")
        self.stdscr.addstr(11, 0, f"成交價: {stock_frame['price']}{stock_mark} ({stock_frame['price_pct_chg']}%)")
        self.stdscr.addstr(12, 0, f"成交量: {stock_frame.get('volume', 'N/A')}")
        self.stdscr.addstr(13, 0, f"最佳買價: {stock_frame['bid_price'][0]} ({stock_frame['bid_pct_chg'][0]}%)")
        self.stdscr.addstr(14, 0, f"最佳賣價: {stock_frame['ask_price'][0]} ({stock_frame['ask_pct_chg'][0]}%)")
        self.stdscr.addstr(15, 0, f"預期價格: {state_dict['expected_price']}")
        self.stdscr.addstr(16, 0, '-'*40)
        self.stdscr.addstr(17, 0, "套利機會")

        # 根據「買賣方向」顯示不同顏色
        if state_dict['action'] == 'buy':
            color_pair = curses.color_pair(1)  # 紅色
        elif state_dict['action'] == 'sell':
            color_pair = curses.color_pair(2)  # 綠色
        else:
            color_pair = curses.color_pair(0)  # 預設顏色

        self.stdscr.addstr(18, 0, f"買賣方向: {action}", color_pair)
        self.stdscr.addstr(19, 0, f"執行價格: {state_dict['action_price']}", color_pair)
        self.stdscr.addstr(20, 0, f"預期利潤: {state_dict['expected_profit']}", color_pair)
        
        self.stdscr.addstr(21, 0, '-'*40)

        # 刷新終端顯示
        self.stdscr.refresh()

    def state_to_debug(self, state):
        # Move to specific position instead of clearing the entire screen
        self.stdscr.move(0, 0)

        # Access 'action' property via dictionary keys
        state_dict = state if isinstance(state, dict) else dict(state)

        stock_frame = state_dict['stock_frame']
        future_frame = state_dict['future_frame']

        # Define stock and future marks based on 'simtrade' and 'is_snapshot' flags
        stock_mark = ' [試搓] ' if stock_frame['simtrade'] else ' [快照] ' if stock_frame['is_snapshot'] else ' '
        future_mark = ' [試搓] ' if future_frame['simtrade'] else ' [快照] ' if future_frame['is_snapshot'] else ' '

        action = '賣出' if state_dict['action'] == 'sell' else '買進' if state_dict['action'] == 'buy' else '無'

        # Get current time
        now = datetime.now()
        if now - self.last_clear > timedelta(seconds=0.1):
            self.stdscr.clear()
            self.last_clear = now

        # General Information
        self.stdscr.addstr(0, 0, f"市場資訊 {now}")
        self.stdscr.addstr(1, 0, '-'*40)

        # Display Taiwan Weighted Index
        self.stdscr.addstr(2, 0, f"台灣加權指數: {future_frame['underlying_price']}")
        self.stdscr.addstr(3, 0, '-'*40)

        # 台指期資訊
        self.stdscr.addstr(4, 0, "台指期資訊")
        self.stdscr.addstr(5, 0, f"時間: {future_frame['timestamp']}")
        self.stdscr.addstr(6, 0, f"台指期現貨同步收盤價: {future_frame['close']}")
        self.stdscr.addstr(7, 0, f"最新成交價: {future_frame['price']}{future_mark} ({future_frame['price_pct_chg']}%)")
        self.stdscr.addstr(8, 0, '-'*40)
        
        # ETN Information
        self.stdscr.addstr(9, 0, "ETN資訊")
        self.stdscr.addstr(10, 0, f"時間: {stock_frame['timestamp']}")
        self.stdscr.addstr(11, 0, f"成交價: {stock_frame['price']}{stock_mark} ({stock_frame['price_pct_chg']}%)")
        self.stdscr.addstr(12, 0, f"成交量: {stock_frame.get('volume', 'N/A')}")
        self.stdscr.addstr(13, 0, f"最佳買價: {stock_frame['bid_price'][0]} ({stock_frame['bid_pct_chg'][0]}%)")
        self.stdscr.addstr(14, 0, f"最佳賣價: {stock_frame['ask_price'][0]} ({stock_frame['ask_pct_chg'][0]}%)")
        self.stdscr.addstr(15, 0, f"預期價格: {state_dict['expected_price']}")
        self.stdscr.addstr(16, 0, '-'*40)
        self.stdscr.addstr(17, 0, "套利機會")

        # Display Buy/Sell action with color
        color_pair = curses.color_pair(1 if state_dict['action'] == 'buy' else 2 if state_dict['action'] == 'sell' else 0)
        self.stdscr.addstr(18, 0, f"買賣方向: {action}", color_pair)
        self.stdscr.addstr(19, 0, f"執行價格: {state_dict['action_price']}", color_pair)
        self.stdscr.addstr(20, 0, f"預期利潤: {state_dict['expected_profit']}", color_pair)
        
        self.stdscr.addstr(21, 0, '-'*40)

        # Display stock top 5 bids and asks on the right side
        right_column = 40  # Adjust based on terminal width

        self.stdscr.addstr(0, right_column, "股票最佳五檔及相關數據")
        self.stdscr.addstr(
                1, right_column,
                f"現價: {stock_frame['price']} ({stock_frame['price_pct_chg']}%), 成交量: {stock_frame['volume']}, "
                f"預期賣出利潤: {state_dict['price_sell_expected_profit']}, "
                f"預期買入利潤: {state_dict['price_buy_expected_profit']}, "
                f"折溢價: {state_dict['price_pod_pct']}%"
            )
        for i in range(5):
            # Bid price row with volume and percentage symbol
            self.stdscr.addstr(
                2 + i, right_column,
                f"買價 {i+1}: {stock_frame['bid_price'][i]} ({stock_frame['bid_pct_chg'][i]}%), 成交量: {stock_frame['bid_volume'][i]}, "
                f"預期利潤: {state_dict['bid_expected_profit'][i]}, 溢價: {state_dict['bid_premium_pct'][i]}%"
            )

            # Ask price row with volume and percentage symbol
            self.stdscr.addstr(
                7 + i, right_column,
                f"賣價 {i+1}: {stock_frame['ask_price'][i]} ({stock_frame['ask_pct_chg'][i]}%), 成交量: {stock_frame['ask_volume'][i]}, "
                f"預期利潤: {state_dict['ask_expected_profit'][i]}, 折價: {state_dict['ask_discount_pct'][i]}%"
            )
        
        # self.stdscr.addstr(33, right_column, '-'*40)

        # Refresh terminal display
        self.stdscr.refresh()

    
