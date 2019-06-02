import logging
import struct

from .berkeley import BerkeleyBase


class Worker(BerkeleyBase):
    def __init__(self, udp):
        BerkeleyBase.__init__(self, udp)
        self.hello_2_server()
        self.waiting_for_manager()

    def hello_2_server(self):
        self.udp.send(b'#')

    def waiting_for_manager(self):
        while True:
            print("TIME:", self.clock.get_clock())
            print("DATE:", self.clock.get_date())
            _data, _ = self.udp.recv()
            try:
                data = struct.unpack('d', _data)[0]
            except (struct.error, ValueError):
                symbol, data = struct.unpack('cd', _data)
            if symbol == b'@':
                self.clock.set_adjustment(data)
                symbol = ''  # clean symbol
            else:
                self.send_difference(data)

    def send_difference(self, data):
        difference = self.clock.get_difference(data)
        _difference = bytearray(struct.pack("d", difference))
        self.udp.send(_difference)
        logging.info("Difference")
        logging.info(difference)
