from douyu.heartbeat_worker import HeartbeatWorker
from douyu.message_worker import MessageWorker
from douyu.tcp_socket import TCPSocket


class Client(object):
    def __init__(self, room_id, heartbeat_interval=45, host='danmuproxy.douyu.com', port=8601):
        self.room_id = room_id
        self.heartbeat_interval = heartbeat_interval
        self.host = host
        self.port = port
        self.tcp_socket = TCPSocket(host=self.host, port=self.port)
        self.heartbeat_worker = HeartbeatWorker(self.tcp_socket)
        self.message_worker = MessageWorker(self.tcp_socket, self.room_id)

    def add_handler(self, msg_type, handler):
        self.message_worker.add_handler(msg_type, handler)

    def refresh_object(self):
        self.tcp_socket = TCPSocket(host=self.host, port=self.port)
        self.message_worker = MessageWorker(self.tcp_socket, self.room_id)
        self.heartbeat_worker = HeartbeatWorker(self.tcp_socket, self.heartbeat_interval)

    def start(self):
        self.tcp_socket.connect()
        self.message_worker.start()
        self.heartbeat_worker.start()


    def stop(self):
        self.message_worker.set_stop()
        self.heartbeat_worker.set_stop()
        self.tcp_socket.close()
        self.refresh_object()
