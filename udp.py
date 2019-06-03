import socket


class Udp:
    def __init__(self, host, port):
        self.dest = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data, **kwargs):
        try:
            self.sock.sendto(data, kwargs['dest'])
        except KeyError:
            self.sock.sendto(data, self.dest)

    def recv(self):
        data, address = self.sock.recvfrom(4096*2)
        return data, address

    def bind(self):
        self.sock.bind(self.dest)

    def __del__(self):
        self.sock.close()
