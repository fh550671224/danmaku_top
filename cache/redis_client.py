import threading
import time

import redis

class RedisClient():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls, *args, **kwargs)
            try:
                # TODO debug only
                # cls._instance.redis_connection = redis.Redis(host='localhost', port=6379)
                cls._instance.redis_connection = redis.Redis(host='my_redis', port=6379)
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

    def get_room_topns(self, room_id, topn):
        c = self.get_redis_connection()
        try:
            danmakus = c.zrevrange(f'danmaku_ranking_{room_id}', 0, topn)
            str_list = [item.decode('utf-8') for item in danmakus]
            return str_list
        except Exception as e:
            print(f'Get Error: {e}')

    def incr(self, keyword, room_id):
        c = self.get_redis_connection()
        try:
            return c.zincrby(f'danmaku_ranking_{room_id}', 1, keyword)
        except Exception as e:
            print(f'Set Error: {e}')

    def get_all_keys(self):
        c = self.get_redis_connection()
        try:
            keys = c.keys('danmaku_ranking_*')
            str_list = [item.decode('utf-8') for item in keys]
            return str_list
        except Exception as e:
            print(f'Get Error: {e}')

    def cron_clear(self):
        def clear():
            c = self.get_redis_connection()
            try:
                keys = self.get_all_keys()
                for key in keys:
                    c.zremrangebyscore(key, '-inf', 20)
            except Exception as e:
                print(f'Cleared Error: {e}')

        while True:
            time.sleep(10*60)
            clear()

    def start_cronjob(self):
        thread = threading.Thread(target=self.cron_clear,daemon=True)
        thread.start()