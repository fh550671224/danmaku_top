import json
import random
import sys
import time

from shared.constants import Constants
from storage.mongo_client import MongoClient
from storage.redis_client import RedisClient


def chatmsg_handler(msg):
    try:
        current_time = int(time.time())
        text = msg['txt']
        room = msg['rid']
        author = msg['nn']
        badge = msg['bnn']

        obj = {
            'text': text,
            'room': room,
            'first_author': author,
            'create_time': current_time,
            'first_author_badge': badge,
            'is_hot': False,
            'last_send_time': current_time,
            'count': 1,
        }
        if len(text) > 10:
            obj['is_hot'] = True

        redis = RedisClient()
        redis.insert(obj)

        # output = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) + msg['nn'] + ": " + msg['txt']
        # print(output)
        # sys.stdout.flush()
    except Exception as e:
        print("chatmsg_handler failed. Exception: %s" % e)
