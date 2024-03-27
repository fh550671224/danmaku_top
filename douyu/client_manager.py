from douyu.client import Client


class ClientManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ClientManager, cls).__new__(cls)
        return cls._instance


    def __init__(self, room_list):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.room_clients_map = {}
            for room in room_list:
                self.add_room(room)


    def add_room(self, room_id):
        if self.room_clients_map.get(room_id) is None:
            c = Client(room_id)
            self.room_clients_map[room_id] = c


