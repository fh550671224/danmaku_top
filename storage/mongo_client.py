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
            print(f'get mongo client Error: {e}')

    def insert(self, collection, obj):
        col = self.get_client()[collection]
        try:
            col.insert_one(obj)

        except Exception as e:
            print(f'mongo Insert Error: {e}')

    def insert_many(self, collection, value_list):
        col = self.get_client()[collection]
        try:
            col.insert_many(value_list)
            print(f'mongo Insert mongo.{collection} Successful: {len(value_list)}')
        except Exception as e:
            print(f'mongo insert_many Error: {e}')

    def find_one_by_text(self, collection, text):
        col = self.get_client()[collection]
        try:
            return col.find_one({'text': text})
        except Exception as e:
            print(f'mongo find_one_by_text Error: {e}')

    def find_many(self, collection, room_id, skip_docs, page_size):
        col = self.get_client()[collection]
        try:
            query = {'room_id': room_id}
            return col.find(query).skip(skip_docs).limit(page_size)
        except Exception as e:
            print(f'mongo find_many Error: {e}')

    def find_many_with_room_id(self, collection, room_id):
        col = self.get_client()[collection]
        try:
            query = {'room_id': room_id}
            docs = col.find(query)
            return docs
        except Exception as e:
            print(f'mongo find_many Error: {e}')

    def archive_danmaku_info(self, text_list):
        col_danmaku_info = self.get_client()[Constants.MONGO_COL_DANMAKU_INFO]
        col_common_danmaku = self.get_client()[Constants.MONGO_COL_COMMON_DAMNAKU]
        try:
            existing_values = set(col_common_danmaku.distinct("text"))

            query = {'text': {'$in': text_list}}
            docs = list(col_danmaku_info.find(query))
            col_danmaku_info.delete_many(query)

            # duplicate check
            docs_to_insert = []
            for doc in docs:
                if doc["text"] in existing_values:
                    continue
                else:
                    docs_to_insert.append(doc)

            # archive
            col_common_danmaku.insert_many(docs_to_insert)
            print(f'archived {len(docs)} danmakus')
        except Exception as e:
            print(f'mongo archive_danmaku_info Error: {e}')

    def get_rooms(self):
        col = self.get_client()['danmaku_rooms']
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

    def get_col_count(self, collection):
        col = self.get_client()[collection]
        try:
            return col.count_documents({})
        except Exception as e:
            print(f'mongo get_col_count Error: {e}')

    def delete_danmaku(self, collection, text):
        col = self.get_client()[collection]
        try:
            return col.delete_one({'text': text})
        except Exception as e:
            print(f'mongo delete_danmaku Error: {e}')
