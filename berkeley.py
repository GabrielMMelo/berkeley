import logging
import time
import threading
import sys
import struct

from clock import Clock

#TODO: testar o cálculo da diferença
#TODO: receber a diferença no manager
# do it better
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

WORKERS_LIMIT = 2
RETRANSMISSION_INTERVAL = 5


class Berkeley:
    def __init__(self, udp):
        self.clock = Clock()
        self.udp = udp


class Worker(Berkeley):
    def __init__(self, udp):
        Berkeley.__init__(self, udp)
        self.hello_2_server()
        self.waiting_for_manager()

    def hello_2_server(self):
        self.udp.send(bytes('#', 'utf-8'))

    def waiting_for_manager(self):
        while True:
            _data, _ = self.udp.recv()
            data = struct.unpack('d', _data)[0]
            logging.info(data)
            self.send_difference(data)

    def send_difference(self, data):
        difference = self.clock.get_difference(data)
        _difference = bytearray(struct.pack("d", difference))
        self.udp.send(_difference)
        logging.info(difference)


class Manager(Berkeley):
    def __init__(self, udp):
        Berkeley.__init__(self, udp)
        self.udp.bind()
        self.workers = []
        self._t = threading.Thread(target=self.receive_workers)
        self._t.start()
        self.loop()

    def loop(self):
        while True:
            time.sleep(RETRANSMISSION_INTERVAL)
            logging.debug('broadcasting...')
            self.broadcast_clock()

    def broadcast_clock(self):
        for worker in self.workers:
            logging.debug(self.clock.get_clock())
            _data = bytearray(struct.pack("d", self.clock.get_clock()))
            self.udp.send(_data, dest=worker)

    def receive_workers(self):
        """
        Parallel method that receives WORKERS_LIMIT number of workers
        and save them addresses
        """
        while len(self.workers) < WORKERS_LIMIT:
            _data, address = self.udp.recv()
            if _data == b'#':
                logging.info("new worker!")
                logging.info(address)
                self.workers.append(address)
        logging.debug('leave receive_workers')

    def calc_average(self):
        pass

    def __del__(self):
        self._t.join()
        logging.debug('exiting')
