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

    @app.route('/danmaku_top/rooms', methods=['GET'])
    def get_danmaku_top():
        mc = MongoClient()
        room_list = mc.get_rooms()
        return {"data": room_list, "total": len(room_list), "msg": "ok"}, 200, {
            'Content-Type': 'application/json'}  # 返回JSON响应

    @app.route('/danmaku_top/<room_id>', methods=['GET'])
    def get_danmaku_top_by_room_id(room_id):
        topn = request.args.get('n')
        if topn is None:
            topn = 10
        rc = RedisClient()
        topn_danmakus = rc.get_room_topn(room_id=room_id, topn=topn)
        return topn_danmakus, 200, {'Content-Type': 'application/json'}

    @app.route('/danmaku_top/rooms', methods=['POST'])
    def add_danmaku_top_room():
        data = request.get_json()
        room_id = data['room_id']

        mc = MongoClient()
        mc.add_room(room_id)

        cm = ClientManager([])
        cm.add_room(room_id)
        c = cm.room_clients_map[room_id]
        c.add_handler('chatmsg', chatmsg_handler)
        c.start()
        return {'msg': 'ok'}, 200, {'Content-Type': ''}

    @app.route('/danmaku_info', methods=['GET'])
    def get_danmaku_info():
        text = request.args.get('text')
        page_size = request.args.get('page_size', type=int, default=20)
        page_num = request.args.get('page_num', type=int, default=1)
        room_id = request.args.get('room_id')
        col = request.args.get('col')
        mongo = MongoClient()
        data = []
        if col is None:
            return {'msg': 'please provide collection name'}, http.client.BAD_REQUEST, {
                'Content-Type': 'application/json'}

        if text is not None:
            doc = mongo.find_one_by_text(Constants.MONGO_COL_DANMAKU_INFO, text)
            if doc is not None:
                doc.pop('_id', None)
                data.append(doc)
        else:
            if room_id is None:
                return {'msg': 'please provide room_id if no text'}, http.client.BAD_REQUEST, {
                    'Content-Type': 'application/json'}
            skip_docs = (page_num - 1) * page_size
            docs = mongo.find_many(col, room_id, skip_docs, page_size)
            for doc in docs:
                doc.pop('_id', None)
                data.append(doc)
        count = mongo.get_col_count(col)

        return {"data": data, "total": count}, 200, {'Content-Type': 'application/json'}
