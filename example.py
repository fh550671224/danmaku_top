import sys
import time

from douyu.client import Client
from redis_client import RedisClient


def chatmsg_handler(msg):
    try:
        redis = RedisClient()
        redis.incr(msg['txt'])

        output = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) + msg['nn'] + ": " + msg['txt']
        print(output)
        sys.stdout.flush()
    except Exception as e:
        print("chatmsg_handler failed. Exception: %s" % e)

c = Client(room_id=9999)
c.add_handler('chatmsg', chatmsg_handler)
# c.add_handler('uenter', uenter_handler)
# c.add_handler('newblackres', newblackres_handler)
redis = RedisClient()
redis.start()
c.start()