import threading
import time

import redis

class RedisClient():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls, *args, **kwargs)
            try:
                cls._instance.redis_connection = redis.Redis(host='localhost', port=6379)
                cls._instance.redis_connection.ping()
                print("Redis Connected")
            except Exception as e:
                print(f'Redis Connection Error: {e}')

        return cls._instance

    def get_redis_connection(self):
        return self._instance.redis_connection

    def get(self, keyword):
        c = self.get_redis_connection()
        try:
            return c.get(keyword)
        except Exception as e:
            print(f'Get Error: {e}')

    def get_tops(self, keyword, topn):
        c = self.get_redis_connection()
        try:
            return c.zrevrange('danmaku_ranking', 0, topn, keyword)
        except Exception as e:
            print(f'Get Error: {e}')

    def incr(self, keyword):
        c = self.get_redis_connection()
        try:
            return c.zincrby('danmaku_ranking', 1, keyword)
        except Exception as e:
            print(f'Set Error: {e}')

    def cron_clear(self):
        def clear():
            c = self.get_redis_connection()
            try:
                c.zremrangebyscore('danmaku_ranking', '-inf', 20)
            except Exception as e:
                print(f'Cleared Error: {e}')

        while True:
            time.sleep(10*60)
            clear()

    def start(self):
        thread = threading.Thread(target=self.cron_clear,daemon=True)
        thread.start()