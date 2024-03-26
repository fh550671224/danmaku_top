import socket
import time


class TCPSocket(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.closed = True

    def close(self):
        if not self.closed:
            self.sock.close()
            self.closed = True

    def send(self, data):
        if self.closed:
            return
        try:
            self.sock.sendall(data)
        except Exception as e:
            self.close()
        return


    def connect(self):
        if self.closed:
            while True:
                try:
                    self.sock.connect((self.host, self.port))
                except Exception as e:
                    self.close()
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    time.sleep(5)
                    continue
                break
            self.closed = False

    def receive(self, target_size):
        data = b''
        while target_size:
            try:
                tmp = self.sock.recv(target_size)
            except Exception as e:
                self.close()
                return None
            if not tmp:
                self.close()
                return None
            target_size -= len(tmp)
            data += tmp
        return data