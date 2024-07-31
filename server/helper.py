import json
import time
from flask import Flask, request, make_response

from storage.redis_client import RedisClient


def filter_danmaku_by_text(text, data):
    res = []
    for v in data:
        if text in v['text']:
            res.append(v)
    return res


def filter_danmaku_hot_only(data):
    res = []
    for v in data:
        if v['is_hot'] == True:
            res.append(v)
    return res


def filter_danmaku_by_trace_back_time(trace_back_time, data):
    res = []

    for v in data:
        if v['create_time'] > trace_back_time:
            res.append(v)
    return res


def filter_danmaku_by_author(author, data):
    res = []

    for v in data:
        if author in v['first_author']:
            res.append(v)
    return res


def sort_danmaku_by_hot(data):
    return data.sort(key=lambda x: x[''])


def check_auth(cookies):
    try:
        session_id = cookies.get('session_id')
        redis = RedisClient()
        obj = redis.get_session(session_id)
        return obj['username'] in ['test']
    except Exception as e:
        return False
