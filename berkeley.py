import logging
import time
import threading
import sys
import struct

from clock import Clock

# do it better
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

WORKERS_LIMIT = 2
RETRANSMISSION_INTERVAL = 5


class Berkeley:
    def __init__(self, udp, is_manager):
        self.udp = udp
        self.is_manager = is_manager
        self.clock = Clock()

        # TODO: Criar uma classe para manager e worker
        if self.is_manager:
            self.udp.bind()
            self.workers = []
            self._t = threading.Thread(target=self.receive_workers)
            self._t.start()
            self.manager_loop()
        else:
            self.hello_2_server()
            self.waiting_for_manager()

    def hello_2_server(self):
        self.udp.send(bytes('#', 'utf-8'))

    def receive_workers(self):
        """
        Parallel method that receives WORKERS_LIMIT number of workers
        and save them addresses
        """
        while len(self.workers) < WORKERS_LIMIT:
            data, address = self.udp.recv()
            if data == b'#':
                logging.info("new worker!")
                logging.info(address)
                self.workers.append(address)
        logging.debug('leave receive_workers')

    def manager_loop(self):
        while True:
            time.sleep(RETRANSMISSION_INTERVAL)
            logging.debug('broadcasting...')
            self.broadcast_clock()

    def broadcast_clock(self):
        for worker in self.workers:
            logging.debug(self.clock.get_clock())
            data = bytearray(struct.pack("d", self.clock.get_clock()))
            self.udp.send(data, dest=worker)

    def waiting_for_manager(self):
        while True:
            data, _ = self.udp.recv()
            data = struct.unpack('d', data)
            logging.info(data)

    def __del__(self):
        if self.is_manager:
            self._t.join()
        logging.debug('exiting')
