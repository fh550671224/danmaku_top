import threading
import time

import redis

from config_handler.config_handler import ConfigHandler
from storage.mongo_client import MongoClient


class RedisClient():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls, *args, **kwargs)
            try:
                # TODO debug only
                config = ConfigHandler()
                if config.is_local_dev():
                    cls._instance.redis_connection = redis.Redis(host='localhost', port=6379, decode_responses=True)
                else:
                    cls._instance.redis_connection = redis.Redis(host='my_redis', port=6379, decode_responses=True)
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

    def get_room_topn(self, room_id, topn):
        c = self.get_redis_connection()
        try:
            return c.zrevrange(f'danmaku_ranking_{room_id}', 0, topn, withscores=True)
        except Exception as e:
            print(f'Get Error: {e}')

    def incr(self, keyword, room_id):
        c = self.get_redis_connection()
        try:
            pipe = c.pipeline(transaction=True)
            pipe.zincrby(f'danmaku_ranking_{room_id}', 1, keyword)
            pipe.execute()
        except Exception as e:
            print(f'Set Error: {e}')

    def get_all_keys(self):
        c = self.get_redis_connection()
        try:
            return c.keys('danmaku_ranking_*')
        except Exception as e:
            print(f'Get Error: {e}')

    def cron_clear(self):
        def clear():
            c = self.get_redis_connection()
            try:
                pipe = c.pipeline(transaction=True)
                keys = self.get_all_keys()
                value_list = []
                for key in keys:
                    tmp = c.zrangebyscore(key, '-inf', 10)
                    value_list.extend(tmp)
                    c.zremrangebyscore(key, '-inf', 10)
                pipe.execute()

                # delete in mongo
                mongo = MongoClient()
                mongo.delete_by_text_list('danmaku_info', value_list)
            except Exception as e:
                print(f'Cleared Error: {e}')

        while True:
            time.sleep(10 * 60)
            clear()

    def start_cronjob(self):
        thread = threading.Thread(target=self.cron_clear, daemon=True)
        thread.start()
