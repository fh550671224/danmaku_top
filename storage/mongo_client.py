import pymongo

from shared.constants import Constants
from config_handler.config_handler import ConfigHandler
from bson.json_util import dumps

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

    def get_rooms(self):
        col = self.get_client()[Constants.MONGO_COL_DANMAKU_ROOMS]
        try:
            # TODO temporaily use this to delete old data
            todo = col.find_one({'name': 'room_list'})
            if todo is not None:
                col.delete_one({'name': 'room_list'})

            res = []
            for room in col.find({},{'_id':False}):
                res.append(room)
            return res
        except Exception as e:
            print(f'mongo get_rooms Error: {e}')

    def add_room(self, obj):
        col = self.get_client()['danmaku_rooms']
        try:
            col.insert_one(obj)
        except Exception as e:
            print(f'mongo add_room Error: {e}')

    def delete_room(self, room):
        col = self.get_client()['danmaku_rooms']
        try:
            col.delete_one({'room': room})
        except Exception as e:
            print(f'mongo add_room Error: {e}')


    def add_user(self, obj):
        col = self.get_client()[Constants.MONGO_COL_USERS]
        try:
            data = col.insert_one(obj)
            return data
        except Exception as e:
            print(f'mongo get_user Error: {e}')

    def get_user(self, username):
        col = self.get_client()[Constants.MONGO_COL_USERS]
        try:
            data = col.find_one({'username':username})
            return data
        except Exception as e:
            print(f'mongo get_user Error: {e}')