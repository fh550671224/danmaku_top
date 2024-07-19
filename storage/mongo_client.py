import pymongo

from shared.constants import Constants
from config_handler.config_handler import ConfigHandler


class MongoClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MongoClient, cls).__new__(cls, *args, **kwargs)
            try:
                config = ConfigHandler()
                if config.is_local_dev():
                    cls._instance.mongo_client = pymongo.MongoClient('localhost', 27017)
                else:
                    cls._instance.mongo_client = pymongo.MongoClient('my_mongo', 27017)
                db = cls._instance.mongo_client.admin
                resp = db.command('ping')
                print(f"mongo Connected. {resp}")
            except Exception as e:
                print(f'mongo Connection Error: {e}')

        return cls._instance

    def get_client(self):
        try:
            return self._instance.mongo_client['danmaku_mongo']
        except Exception as e:
            print(f'mongo get_client Error: {e}')

    def insert_danmaku(self, obj):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        try:
            col.insert_one(obj)

        except Exception as e:
            print(f'mongo insert_danmaku Error: {e}')

    def insert_many(self, value_list):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        try:
            col.insert_many(value_list)
            print(f'mongo insert_many Successful: {len(value_list)}')
        except Exception as e:
            print(f'mongo insert_many Error: {e}')

    def find_one_danmaku(self, text, room):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        try:
            return col.find_one({'text': text, 'room': room})
        except Exception as e:
            print(f'mongo find_one_by_text Error: {e}')

    def find_many_danmaku(self, room, skip_docs, page_size):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        try:
            query = {'room': room}
            return col.find(query).skip(skip_docs).limit(page_size)
        except Exception as e:
            print(f'mongo find_many_danmaku Error: {e}')

    def update_danmaku(self, obj):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        try:
            room = obj['room']
            text = obj['text']
            col.find_one_and_update({'room': room, 'text': text}, {'$set': obj}, upsert=True)
        except Exception as e:
            print(f'mongo update_danmaku Error: {e}')

    def archive_danmaku(self, text_list):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        try:
            query = {'text': {'$in': text_list}}
            col.update_many(query, {'$set': {'is_hot': False}})
            print(f'archived {len(text_list)} danmakus')
        except Exception as e:
            print(f'mongo archive_danmaku Error: {e}')

    def get_rooms(self):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_ROOMS]
        try:
            query = {'name': 'room_list'}
            data = col.find_one(query)
            if data is None:
                return []
            else:
                rooms = data['rooms']
                return rooms
        except Exception as e:
            print(f'mongo get_rooms Error: {e}')

    def add_room(self, room):
        col = self.get_client()['danmaku_rooms']
        try:
            data = col.find_one({'name': 'room_list'})
            if data is None:
                col.insert_one({'name': 'room_list', 'rooms': [room]})
            else:
                col.update_one({'name': 'room_list'}, {'$push': {'rooms': room}})
        except Exception as e:
            print(f'mongo add_room Error: {e}')

    def get_danmaku_count(self, room):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        try:
            return col.count_documents({'room': room})
        except Exception as e:
            print(f'mongo get_danmaku_count Error: {e}')

    def delete_danmaku(self, collection, text):
        col = self.get_client()[collection]
        try:
            return col.delete_one({'text': text})
        except Exception as e:
            print(f'mongo delete_danmaku Error: {e}')
