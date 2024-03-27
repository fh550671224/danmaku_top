import sys
import time

from cache.redis_client import RedisClient


def chatmsg_handler(msg):
    try:
        redis = RedisClient()
        redis.incr(msg['txt'], msg['rid'])

        output = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) + msg['nn'] + ": " + msg['txt']
        print(output)
        sys.stdout.flush()
    except Exception as e:
        print("chatmsg_handler failed. Exception: %s" % e)

