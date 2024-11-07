import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone
import os

# 台北時區
tz = timezone('Asia/Taipei')

process = None

def run_python_file():
    """運行指定的 Python 檔案"""
    os.system('git pull')
    global process
    process = subprocess.Popen(['python', 'bot.py'])
    print("程式已啟動。")

def stop_and_restart_python_file():
    """停止當前進程並重新啟動"""
    global process
    if process:
        process.terminate()
        process.wait()
        print("程式已停止。")
    run_python_file()  # 重新啟動程式

if __name__ == "__main__":
    # 初始化阻塞型調度器
    scheduler = BlockingScheduler(timezone=tz)

    # 設置每天的 7:00 和 14:00 根據台北時區執行重啟任務
    scheduler.add_job(stop_and_restart_python_file, 'cron', hour=7, minute=0, timezone=tz)
    scheduler.add_job(stop_and_restart_python_file, 'cron', hour=15, minute=0, timezone=tz)
    scheduler.add_job(stop_and_restart_python_file, 'cron', hour=2, minute=0, timezone=tz)

    # 先啟動程式
    run_python_file()

    # 啟動調度器
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        if process:
            process.terminate()
