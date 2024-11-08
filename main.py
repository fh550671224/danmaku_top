import json
import sys
import time

from config_handler.config_handler import ConfigHandler
from douyu.client import Client
from storage.mongo_client import MongoClient
from storage.redis_client import RedisClient
from flask import Flask, request

from douyu.client_manager import ClientManager
from server.routers import _app, register_routers
from server.handlers import chatmsg_handler
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    # 执行初始化逻辑
    print("Performing initial setup...")
    config = ConfigHandler()

    mongo = MongoClient()
    room_list = mongo.get_rooms()

    redis = RedisClient()
    redis.start_cronjob(room_list)

    cm = ClientManager(room_list)
    for key, value in cm.room_clients_map.items():
        value.add_handler('chatmsg', chatmsg_handler)
        value.start()

    register_routers(app)

    return app


if __name__ == '__main__':
    config = ConfigHandler()

    mongo = MongoClient()
    room_list = mongo.get_rooms()

    redis = RedisClient()
    redis.start_cronjob(room_list)

    cm = ClientManager(room_list)
    for key, value in cm.room_clients_map.items():
        value.add_handler('chatmsg', chatmsg_handler)
        value.start()

    register_routers(_app)
    _app.run(host='0.0.0.0')