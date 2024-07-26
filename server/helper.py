import json
import time


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