import json

from storage.redis_client import RedisClient
from flask import Flask, request

from douyu.client_manager import ClientManager
from .handlers import chatmsg_handler

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello, Flask!'


@app.route('/danmaku_top', methods=['GET'])
def get_danmaku_top():
    rc = RedisClient()
    keys = rc.get_all_keys()
    if len(keys) == 0:
        return 'Nothing yet'
    else:
        json_data = json.dumps(keys)
        return json_data, 200, {'Content-Type': 'application/json'}  # 返回JSON响应


@app.route('/danmaku_top/<room_id>', methods=['GET'])
def get_danmaku_top_by_room_id(room_id):
    topn = request.args.get('n')
    if topn is None:
        topn = 10
    rc = RedisClient()
    topn_danmakus = rc.get_room_topn(room_id=room_id, topn=topn)
    return topn_danmakus, 200, {'Content-Type': ''}


@app.route('/danmaku_top', methods=['POST'])
def add_danmaku_top_room():
    data = request.get_json()
    room_id = data['room_id']
    cm = ClientManager([])
    cm.add_room(room_id)
    c = cm.room_clients_map[room_id]
    c.add_handler('chatmsg', chatmsg_handler)
    c.start()
    return {'msg': 'ok'}, 200, {'Content-Type': ''}