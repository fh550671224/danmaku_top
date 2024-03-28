import json
import sys
import time

from douyu.client import Client
from storage.mongo_client import MongoClient
from storage.redis_client import RedisClient
from flask import Flask, request

from douyu.client_manager import ClientManager
from server.routers import app
from server.handlers import chatmsg_handler


def get_room_ids():
    rc = RedisClient()
    keys = rc.get_all_keys()
    room_list = []
    for key in keys:
        splited = str.split(key, '_')
        if len(splited) != 3:
            print(f'Error: key({key}) split failed.')
            continue
        room_id = splited[2]
        room_list.append(room_id)
    return room_list


if __name__ == '__main__':
    redis = RedisClient()
    redis.start_cronjob()
    mongo = MongoClient()
    room_list = get_room_ids()
    cm = ClientManager(room_list)
    for key, value in cm.room_clients_map.items():
        value.add_handler('chatmsg', chatmsg_handler)
        value.start()
    app.run(host='0.0.0.0')
