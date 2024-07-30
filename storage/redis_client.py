import json
import threading
import time

import redis

from config_handler.config_handler import ConfigHandler
from shared.constants import Constants
from storage.mongo_client import MongoClient


class RedisClient():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls, *args, **kwargs)
            try:
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

    def get(self, text, room):
        c = self.get_redis_connection()
        try:
            q = f'{room}_{text}'
            return c.get(q)
        except Exception as e:
            print(f'Redis get Error: {e}')

    def insert(self, obj):
        c = self.get_redis_connection()
        try:
            text = obj['text']
            room = obj['room']
            current_time = int(time.time())

            key = f'{room}_{text}'

            data = c.get(key)
            if data is not None:
                data_parsed = json.loads(data)
                data_parsed['last_send_time'] = current_time
                data_parsed['count'] = data_parsed['count'] + 1
                dump = json.dumps(data_parsed)
                c.set(key, dump)
            else:
                obj_dump = json.dumps(obj)
                c.set(key, obj_dump)

        except Exception as e:
            print(f'Redis insert Error: {e}')

    def get_room_kvs(self, room):
        c = self.get_redis_connection()
        try:
            match = f'{room}_*'
            keys = c.keys(match)

            values = c.mget(keys)
            kv_pairs = {key: value for key, value in zip(keys, values)}
            return kv_pairs
        except Exception as e:
            print(f'Redis get_room_kvs Error: {e}')

    def delete_danmaku(self, room, text):
        c = self.get_redis_connection()
        try:
            key = f'{room}_{text}'
            pipe = c.pipeline(transaction=True)
            pipe.delete(key)
            pipe.execute()
        except Exception as e:
            print(f'Redis delete_danmaku Error: {e}')

    def update_danmaku(self, room, text, obj):
        c = self.get_redis_connection()
        try:
            key = f'{room}_{text}'
            c.set(key, json.dumps(obj))
        except Exception as e:
            print(f'Redis update_danmaku Error: {e}')

    def cron_clear_danmaku(self, room):
        def clear_danmaku(room):
            c = self.get_redis_connection()
            try:
                kvs = self.get_room_kvs(room)
                pipe = c.pipeline(transaction=True)
                for key, value in kvs.items():
                    value = json.loads(value)

                    if value['count'] < 10:
                        if value['count'] <= 3:
                            pipe.delete(key)
                        else:
                            if not value['is_hot']:
                                continue
                            value['is_hot'] = False
                            dump = json.dumps(value)
                            pipe.set(key, dump)
                pipe.execute()

            except Exception as e:
                print(f'Redis cron_clear_danmaku Error: {e}')

        while True:
            time.sleep(10 * 60)
            clear_danmaku(room)

    def start_cronjob(self, room_list):
        for room in room_list:
            thread = threading.Thread(target=self.cron_clear_danmaku, args=(room,), daemon=True)
            thread.start()


    def insert_session(self, session_id, value):
        c = self.get_redis_connection()
        try:
            key = f'session_{session_id}'
            c.set(key, json.dumps(value), ex=30*60)
        except Exception as e:
            print(f'Redis insert_session Error: {e}')

    def get_session(self, session_id):
        c = self.get_redis_connection()
        try:
            key = f'session_{session_id}'
            return c.get(key)
        except Exception as e:
            print(f'Redis insert_session Error: {e}')