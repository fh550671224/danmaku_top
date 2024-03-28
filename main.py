import json
import sys
import time

from config_handler.config_handler import ConfigHandler
from douyu.client import Client
from storage.mongo_client import MongoClient
from storage.redis_client import RedisClient
from flask import Flask, request

from douyu.client_manager import ClientManager
from server.routers import app
from server.handlers import chatmsg_handler


@app.before_first_request
def initialize():
    config = ConfigHandler()

    redis = RedisClient()
    redis.start_cronjob()

    mongo = MongoClient()

    room_list = mongo.get_rooms()
    cm = ClientManager(room_list)
    for key, value in cm.room_clients_map.items():
        value.add_handler('chatmsg', chatmsg_handler)
        value.start()


if __name__ == '__main__':
    config = ConfigHandler()

    redis = RedisClient()
    redis.start_cronjob()

    mongo = MongoClient()

    room_list = mongo.get_rooms()
    cm = ClientManager(room_list)
    for key, value in cm.room_clients_map.items():
        value.add_handler('chatmsg', chatmsg_handler)
        value.start()

    app.run(host='0.0.0.0')
