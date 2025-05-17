# ETN Arbitrage
## 功能介紹
### Bot channel
![bot channel](https://github.com/ryanovovo/ETN-Arbitrage/blob/main/bot%20channel.jpeg)

使用者可透過互動式按鈕操作，查詢以下資訊：

* 套利資訊：顯示目前市場狀況與是否存在套利機會。
* API 狀態：顯示 API 使用情形，包括：
  * API 流量使用狀況
  * 是否在接收股票即時資料
  * 是否正在進行資料串流（股票即時套利資訊每 5 秒更新一次）


### 即時資訊 channel
![stream channel](https://github.com/ryanovovo/ETN-Arbitrage/blob/main/stream.jpeg)

系統每 5 秒自動更新一次，提供完整的市場與套利資訊，包括：
* 台指期資訊：
    * 最新成交價與漲跌幅
    * 同步的期貨收盤價
* ETN 資訊：
    * 成交價、成交量
    * 最佳買賣價與預期價格
* 套利機會：
    * 套利方向（買入或賣出）
    * 執行價格與預期利潤

### 套利通知 channel
![webhook channel](https://github.com/ryanovovo/ETN-Arbitrage/blob/main/webhook%20notification.jpeg)

當系統偵測到套利機會「出現」或「消失」，會立即推播通知，內容包括當下的市場數據與套利資訊，讓用戶即時應對市場變化。

## 安裝與執行說明

### 1. 建立 Conda 環境
```
conda create -n etn python=3.12
conda activate etn
```

### 2. 安裝套件
```
pip install -r requirements.txt
```

### 3. 建立 .env 檔案
在專案根目錄建立 .env 檔案，填入以下內容：
```
SINOTRADE_API_KEY = 'SINOTRADE_API_KEY'
SINOTRADE_SECRET_KEY = 'SINOTRADE_SECRET_KEY'
DISCORD_BOT_TOKEN = 'DISCORD_BOT_TOKEN'
WEBHOOK_URL = 'WEBHOOK_CHANNEL_URL'
DISCORD_CHANNEL_ID = DISCORD_CHANNEL_ID
WEBHOOK_CHANNEL_ID = WEBHOOK_CHANNEL_ID
STREAM_CHANNEL_ID = STREAM_CHANNEL_ID
```

### 4. 啟動機器人
```
python main.py
```





