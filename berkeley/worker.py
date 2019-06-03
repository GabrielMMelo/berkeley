import logging as log
import struct
import sys

from .berkeley import BerkeleyBase

log.basicConfig(stream=sys.stdout, level=log.DEBUG)


class Worker(BerkeleyBase):
    def __init__(self, udp):
        BerkeleyBase.__init__(self, udp)
        self.hello_2_server()
        self.waiting_for_manager()

    def hello_2_server(self):
        """
        """
        self.udp.send(b'#')

    def waiting_for_manager(self):
        """
        """
        while True:
            # log.info("TIME:")
            # log.info(self.clock.get_clock())
            # log.info("DATE:")
            # log.info(self.clock.get_date())
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
                log.debug('----------------------------')

    def send_difference(self, data):
        """
        """
        difference = self.clock.get_difference(data)
        _difference = bytearray(struct.pack("d", difference))
        self.udp.send(_difference)
        log.info("Difference (ms)")
        log.info(difference)
