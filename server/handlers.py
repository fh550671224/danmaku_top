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
        room_id = msg['rid']
        author = msg['nn']
        badge = msg['bnn']

        mongo = MongoClient()
        obj = {
            'text': text,
            'room_id': room_id,
            'first_author': author,
            'create_time_stamp': current_time,
            'first_author_badge': badge,
        }

        if len(text) > 15:

            redis = RedisClient()
            redis.incr(text, room_id)

            exist = mongo.find_one_by_text(Constants.MONGO_COL_DANMAKU_INFO, text)
            if exist is None:
                mongo.insert(Constants.MONGO_COL_DANMAKU_INFO, obj)

        # take 1/10 sample and insert into common collection
        rand = random.randint(0, 999)
        if rand == 1:
            mongo.insert(Constants.MONGO_COL_COMMON_DAMNAKU, obj)

        # output = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) + msg['nn'] + ": " + msg['txt']
        # print(output)
        # sys.stdout.flush()
    except Exception as e:
        print("chatmsg_handler failed. Exception: %s" % e)
