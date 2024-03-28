import sys
import time

from storage.mongo_client import MongoClient
from storage.redis_client import RedisClient


def chatmsg_handler(msg):
    try:
        current_time = int(time.time())
        text = msg['txt']
        room_id = msg['rid']
        author = msg['nn']
        badge = msg['bnn']

        if len(text) > 10:
            obj = {
                'text': text,
                'room_id': room_id,
                'first_author': author,
                'create_time_stamp': current_time,
                'first_author_badge': badge,
            }
            redis = RedisClient()
            redis.incr(text, room_id)

            mongo = MongoClient()
            exist = mongo.find_one_by_text('danmaku_info', text)
            if exist is None:
                mongo.insert('danmaku_info', obj)

        output = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) + msg['nn'] + ": " + msg['txt']
        print(output)
        sys.stdout.flush()
    except Exception as e:
        print("chatmsg_handler failed. Exception: %s" % e)
