import pymongo


class MongoClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MongoClient, cls).__new__(cls, *args, **kwargs)
            try:
                # TODO debug only
                # cls._instance.mongo_client = pymongo.MongoClient('localhost', 27017)
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

    def find_one_by_text(self, collection, text):
        col = self.get_client()[collection]
        try:
            return col.find_one({'text': text})
        except Exception as e:
            print(f'mongo find_one_by_text Error: {e}')

    def delete_by_text_list(self, collection, text_list):
        col = self.get_client()[collection]
        try:
            query = {'text': {'$in': text_list}}
            col.delete_many(query)
        except Exception as e:
            print(f'mongo delete_by_text_list Error: {e}')
