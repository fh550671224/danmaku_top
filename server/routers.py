import http.client
import json

from config_handler.config_handler import ConfigHandler
from storage.mongo_client import MongoClient
from storage.redis_client import RedisClient
from flask import Flask, request
from flask_cors import CORS

from shared.constants import Constants
from douyu.client_manager import ClientManager
from .handlers import chatmsg_handler

_app = Flask(__name__)
CORS(_app)


def register_routers(app):
    @app.route('/')
    def home():
        return 'Hello, Flask!'

    @app.route('/api/rooms', methods=['GET'])
    def get_danmaku_top():
        mc = MongoClient()
        room_list = mc.get_rooms()
        return {"data": room_list, "total": len(room_list), "msg": "ok"}, 200, {
            'Content-Type': 'application/json'}  # 返回JSON响应

    @app.route('/api/danmaku/<room>', methods=['GET'])
    def get_danmaku(room):
        topn = request.args.get('n')
        text = request.args.get('text')
        hot_only = request.args.get('hot_only')

        redis = RedisClient()

        kvs = redis.get_room_kvs(room)
        data = []
        for k, v in kvs.items():
            v = json.loads(v)
            if text is not None:
                if text in v['text']:
                    data.append(v)
            else:
                data.append(v)

        if hot_only == 'true':
            d = []
            for v in data:
                if v['is_hot'] == True:
                    d.append(v)
            data = d

        data.sort(key=lambda x: x['count'], reverse=True)

        return data[:int(topn)], 200, {'Content-Type': 'application/json'}

    @app.route('/api/danmaku/<room>', methods=['PUT'])
    def update_danmaku(room):
        obj = request.get_json()

        redis = RedisClient()

        record = redis.get(obj['text'], room)
        if record is None:
            return {'msg': 'record not found'}, http.client.BAD_REQUEST, {
                'Content-Type': 'application/json'}

        redis.update_danmaku(room, obj['text'], obj)
        return {'msg': 'ok'}, 200, {'Content-Type': ''}

    @app.route('/api/delete_danmaku', methods=['POST'])
    def delete_danmaku():
        obj = request.get_json()

        redis = RedisClient()

        record = redis.get(obj['text'], obj['room'])
        if record is None:
            return {'msg': 'record not found'}, http.client.BAD_REQUEST, {
                'Content-Type': 'application/json'}

        redis.delete_danmaku(obj['room'], obj['text'])
        return {'msg': 'ok'}, 200, {'Content-Type': ''}

    @app.route('/api/rooms', methods=['POST'])
    def add_room_hanlder():
        data = request.get_json()
        room = data['room']

        mongo = MongoClient()
        mongo.add_room(room)

        cm = ClientManager([])
        cm.add_room(room)
        c = cm.room_clients_map[room]
        c.add_handler('chatmsg', chatmsg_handler)
        c.start()
        return {'msg': 'ok'}, 200, {'Content-Type': ''}
