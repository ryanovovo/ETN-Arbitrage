from typing import Optional
from backend.utils import get_snapshot, get_data_type, get_nearmonth_future_code
import redis
import subprocess
from backend.serial import serialize, deserialize
import time

class DataManager:
    def __init__(self, api, max_data_size=100):
        self.api = api
        self.max_data_size = max_data_size
        # self.redis_server_path = '/opt/homebrew/opt/redis/bin/redis-server'
        self.redis_config_path = './redis.conf'
        redis_subprocess = subprocess.Popen(['redis-server', self.redis_config_path])
        self.r = None
        while self.r is None:
            try:
                self.r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
                self.r.ping()
            except redis.ConnectionError:
                # 如果连接失败，等待一段时间后重试
                time.sleep(1)  # 每次等待 1 秒钟
        self.r.flushdb()

    def subscribe(self, code: str, category: str, data_type: str):
        if self.__is_subscribed(code, category, data_type):
            raise ValueError(
                f"Code {code} is already subscribed to {category} {data_type}"
            )
        subscribed_key = f"subscribed:{category}:{data_type}"
        assert self.r.sadd(subscribed_key, code) == 1
        storage_key = f"storage:{code}:{category}:{'snapshot'}"
        snapshot = get_snapshot(self.api, code, category)
        serialized_snapshot = serialize(snapshot, category, 'snapshot')
        self.r.xadd(storage_key, {'data': serialized_snapshot}, maxlen=self.max_data_size, approximate=True)
       
    
    def unsubscribe(self, code: str, category: str, data_type: str):
        if not self.__is_subscribed(code, category, data_type):
            raise ValueError(
                f"Code {code} is not subscribed to {category} {data_type}"
            )
        subscribed_key = f"subscribed:{category}:{data_type}"
        assert self.r.srem(subscribed_key, code) == 1
        storage_key = f"storage:{code}:{category}:{data_type}"
        assert self.r.delete(storage_key) == 1

    def add_data(self, data):
        data_type, category = get_data_type(data)
        code = data.code
        self.__add_data(code, category, data_type, data)

    def get_data(self, code: str,
                 category: str,
                 data_type: str,
                 size: Optional[int] = None):
        storage_key = f"storage:{code}:{category}:{data_type}"
        data = self.r.xrange(storage_key, min='-', max='+')
        data = [deserialize(x[1]) for x in data]
        if size > self.max_data_size:
            raise ValueError(
                f"Size {size} exceeds maximum size {self.max_data_size}"
            )
        if not self.__is_empty(code, category, data_type):
            raise ValueError(
                f"Code {code} has no {category} {data_type} data"
            )
        if size > len(data):
            raise ValueError(
                f"Size {size} exceeds available data size "
                f"{len(data)}"
            )

        if size is not None:
            return data[-size:]
        return data

    def get_latest_data(self, code: str,
                    category: str,
                    data_type: str,
                    snapshot: bool = True):
        storage_key = f"storage:{code}:{category}:{data_type}"
        if self.__is_empty(code, category, data_type):
            if snapshot:
                snapshot = self.r.xrevrange(storage_key, count=1)
                snapshot = snapshot[0][1]
                snapshot = deserialize(snapshot)
                return snapshot
            raise ValueError(
                f"Code {code} has no {category} {data_type} data"
            )
        data = self.r.xrevrange(storage_key, count=1)[0][1]
        data = deserialize(data)
        return data

    def __is_subscribed(self, code: str, category: str, data_type: str):
        subscribed_key = f"subscribed:{category}:{data_type}"
        return self.r.sismember(subscribed_key, code)

    def __add_data(self, code: str, category: str, data_type: str, data):
        if category == 'fop':
            near_month_future_code = get_nearmonth_future_code(self.api, code)
            if code == near_month_future_code:
                code = code[:3] + 'R1'
        if not self.__is_subscribed(code, category, data_type):
            raise ValueError(
                f"Code {code} is not subscribed to {category} {data_type}"
            )
        storage_key = f"storage:{code}:{category}:{data_type}"
        serialized_data = serialize(data, category, data_type)
        self.r.xadd(storage_key, {'data': serialized_data}, maxlen=self.max_data_size, approximate=True)

    def __is_empty(self, code: str, category: str, data_type: str):
        storage_key = f"storage:{code}:{category}:{data_type}"
        return not self.r.exists(storage_key)
