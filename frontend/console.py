import curses
from datetime import datetime, timedelta

class ConsoleManager:
    def __init__(self, padding_length=10):
        self.stdscr = curses.initscr()
        curses.curs_set(0)  # 隱藏游標
        self.padding = ' ' * padding_length  # 設置空格填充
        self.last_clear = datetime.now()

        # 初始化顏色組合
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # 紅色
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 綠色

    def close_dynamic_print(self):
        # 結束 curses 操作並恢復終端
        if self.stdscr:
            curses.endwin()

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
        self.stdscr.addstr(0, 0, f"市場資訊 {now}{self.padding}")
        self.stdscr.addstr(1, 0, '-'*40)

        # 新增台灣加權指數顯示
        self.stdscr.addstr(2, 0, f"台灣加權指數: {future_frame['underlying_price']}{self.padding}")

        # 加入分隔線
        self.stdscr.addstr(3, 0, '-'*40 + self.padding)
        
        self.stdscr.addstr(4, 0, "台指期資訊" + self.padding)
        self.stdscr.addstr(5, 0, f"時間: {future_frame['timestamp']}{self.padding}")
        self.stdscr.addstr(6, 0, f"台指期現貨同步收盤價: {future_frame['close']}{self.padding}")
        self.stdscr.addstr(7, 0, f"最新成交價: {future_frame['price']}{future_mark} ({future_frame['price_pct_chg']}%){self.padding}")
        self.stdscr.addstr(8, 0, '-'*40)
        self.stdscr.addstr(9, 0, "ETN資訊" + self.padding)
        self.stdscr.addstr(10, 0, f"時間: {stock_frame['timestamp']}{self.padding}")
        self.stdscr.addstr(11, 0, f"成交價: {stock_frame['price']}{stock_mark} ({stock_frame['price_pct_chg']}%){self.padding}")
        self.stdscr.addstr(12, 0, f"成交量: {stock_frame.get('volume', 'N/A')}{self.padding}")
        self.stdscr.addstr(13, 0, f"最佳買價: {stock_frame['best_bid']} ({stock_frame['bid_pct_chg']}%){self.padding}")
        self.stdscr.addstr(14, 0, f"最佳賣價: {stock_frame['best_ask']} ({stock_frame['ask_pct_chg']}%){self.padding}")
        self.stdscr.addstr(15, 0, f"預期價格: {state_dict['expected_price']}{self.padding}")
        self.stdscr.addstr(16, 0, '-'*40)
        self.stdscr.addstr(17, 0, "套利機會" + self.padding)

        # 根據「買賣方向」顯示不同顏色
        if state_dict['action'] == 'buy':
            color_pair = curses.color_pair(1)  # 紅色
        elif state_dict['action'] == 'sell':
            color_pair = curses.color_pair(2)  # 綠色
        else:
            color_pair = curses.color_pair(0)  # 預設顏色

        self.stdscr.addstr(18, 0, f"買賣方向: {action}{self.padding}", color_pair)
        self.stdscr.addstr(19, 0, f"執行價格: {state_dict['action_price']}{self.padding}", color_pair)
        self.stdscr.addstr(20, 0, f"預期利潤: {state_dict['expected_profit']}{self.padding}", color_pair)
        
        self.stdscr.addstr(21, 0, '-'*40)

        # 刷新終端顯示
        self.stdscr.refresh()
