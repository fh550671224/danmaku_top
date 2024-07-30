import http.client
import json

import flask

from config_handler.config_handler import ConfigHandler
from shared.utils import generate_hash
from storage.mongo_client import MongoClient
from storage.redis_client import RedisClient
from flask import Flask, request, make_response
from flask_cors import CORS

from shared.constants import Constants
from douyu.client_manager import ClientManager
from .handlers import chatmsg_handler
from .helper import filter_danmaku_by_text, filter_danmaku_hot_only, filter_danmaku_by_trace_back_time, \
    filter_danmaku_by_author

_app = Flask(__name__)
CORS(_app, supports_credentials=True)


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
        # topn = request.args.get('n')
        text = request.args.get('text')
        # hot_only = request.args.get('hot_only')
        trace_back_time = request.args.get('trace_back_time')
        author = request.args.get('author')
        hot_first = request.args.get('hot_first')

        redis = RedisClient()

        kvs = redis.get_room_kvs(room)
        data = []
        for k, v in kvs.items():
            v = json.loads(v)
            data.append(v)

        if author is not None:
            data = filter_danmaku_by_author(author, data)

        if text is not None:
            data = filter_danmaku_by_text(text, data)

        # if hot_only == 'true':
        #     data = filter_danmaku_hot_only(data)

        if trace_back_time is not None:
            data = filter_danmaku_by_trace_back_time(int(trace_back_time), data)

        data.sort(key=lambda x: x['count'], reverse=True)

        if hot_first == 'true':
            data.sort(key=lambda x: x['is_hot'], reverse=True)

        # return data[:int(topn)], 200, {'Content-Type': 'application/json'}
        return data, 200, {'Content-Type': 'application/json'}

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

    @app.route('/api/login', methods=['POST'])
    def login_hanlder():
        data = request.get_json()
        username = data['username']
        password = data['password']

        mongo = MongoClient()
        user = mongo.get_user(username)
        if user is None:
            return {'msg': 'user not found'}, 200, {'Content-Type': 'application/json'}

        if password != user['password']:
            return {'msg': 'incorrect password'}, 200, {'Content-Type': 'application/json'}

        session_id = generate_hash(username)
        resp = make_response({'msg': 'ok'}, 200)
        resp.headers['Content-Type'] = 'application/json'
        resp.set_cookie('session_id', session_id, max_age=30*60)

        redis = RedisClient()
        s = redis.get_session(session_id)
        if s is not None:
            return resp

        redis.insert_session(session_id, {'username': username})

        return resp

    @app.route('/api/register', methods=['POST'])
    def register_hanlder():
        data = request.get_json()
        username = data['username']

        mongo = MongoClient()
        user = mongo.get_user(username)
        if user is not None:
            return {'msg': 'user already exists'}, 200, {'Content-Type': 'application/json'}
        mongo.add_user(data)

        session_id = generate_hash(username)
        resp = make_response({'msg': 'ok'}, 200)
        resp.headers['Content-Type'] = 'application/json'
        resp.set_cookie('session_id', session_id, max_age=30*60)

        redis = RedisClient()
        redis.insert_session(session_id, {'username': username})

        return resp
