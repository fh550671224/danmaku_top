import time
from threading import Thread
from . import utils

class HeartbeatWorker(Thread):
    def __init__(self, sock, heartbeat_interval=45):
        Thread.__init__(self)
        self.need_stop = False
        self.sock = sock
        self.heartbeat_interval = heartbeat_interval

    def set_stop(self, need_stop=True):
        self.need_stop = need_stop

    def run(self):
        while not self.need_stop:
            ori_str = utils.assemble_heartbeat_str()
            data = utils.assemble_transfer_data(ori_str)
            self.sock.send(data)
            time.sleep(self.heartbeat_interval)
