import logging
import queue
from threading import Thread

from douyu import utils
from douyu.message_consumer import MessageConsumer


class MessageWorker(Thread):
    def __init__(self, sock, room_id):
        Thread.__init__(self)
        self.need_stop = False
        self.sock = sock
        self.room_id = room_id
        self.msg_queue = queue.Queue()
        self.message_consumer = MessageConsumer(self.msg_queue)

    def set_stop(self, need_stop=True):
        self.need_stop = need_stop
        self.message_consumer.set_stop(need_stop)

    def add_handler(self, msg_type, handler):
        self.message_consumer.add_handler(msg_type,handler)


    def prepare(self):
        self.message_consumer.start()
        self.enter_room()


    def enter_room(self):
        ori_str = utils.assemble_login_str(self.room_id)
        data = utils.assemble_transfer_data(ori_str)
        self.sock.send(data)
        ori_str = utils.assemble_join_group_str(self.room_id)
        data = utils.assemble_transfer_data(ori_str)
        self.sock.send(data)


    def run(self):
        self.prepare()
        while not self.need_stop:
            packet_size = self.sock.receive(4)
            if packet_size is None:
                logging.warning("Socket closed")
                self.sock.connect()
                self.enter_room()
                continue

            packet_size = int.from_bytes(packet_size, byteorder='little')
            data = self.sock.receive(packet_size)
            if data is None:
                logging.warning("Socket closed")
                self.sock.connect()
                self.enter_room()
                continue
            self.msg_queue.put(data)

