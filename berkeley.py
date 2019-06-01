import logging
import time
import threading
import sys
import struct

from clock import Clock

#TODO: Limitar a um Manager
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
            print("TIME:", self.clock.get_clock())
            print("DATE:", self.clock.get_date())
            _data, _ = self.udp.recv()
            try:
                data = struct.unpack('d', _data)[0]
            except (struct.error, ValueError):
                symbol, data = struct.unpack('cd', _data)
            if symbol== b'@':
                self.clock.set_adjustment(data)
                symbol = ''
            else:
                self.send_difference(data)

    def send_difference(self, data):
        difference = self.clock.get_difference(data)
        _difference = bytearray(struct.pack("d", difference))
        self.udp.send(_difference)
        logging.info("Difference")
        logging.info(difference)


class Manager(Berkeley):
    def __init__(self, udp):
        Berkeley.__init__(self, udp)
        self.udp.bind()
        self.workers = {}
        self._t = threading.Thread(target=self.receive_workers)
        self._t.start()
        self.loop()

    def loop(self):
        while True:
            print("TIME:", self.clock.get_clock())
            print("DATE:", self.clock.get_date())
            logging.debug('broadcasting...')
            self.broadcast_clock()
            time.sleep(RETRANSMISSION_INTERVAL)
            self.update_clocks()

    def broadcast_clock(self):
        """ Send manager's clock to another workers """
        for address, _ in self.workers.items():
            _data = bytearray(struct.pack("d", self.clock.get_clock()))
            self.udp.send(_data, dest=address)

    def receive_workers(self):
        """
        Parallel method that receives WORKERS_LIMIT number of workers
        and save them addresses
        """
        #TODO: Pensar melhor o limite daqui
        while len(self.workers) <= WORKERS_LIMIT:
            _data, address = self.udp.recv()
            if _data == b'#':
                logging.info("New worker!")
                logging.info(address)
                self.workers[address] = 0
            else:
                data = struct.unpack('d', _data)[0]
                self.workers[address] = data  # refresh difference
        logging.debug('leave receive_workers')

    def update_clocks(self):
        average = self.average_calc()
        logging.info("Average")
        logging.info(average)
        self.clock.set_adjustment(average)  # update manager clock
        for address, difference in self.workers.items():
            adjustment = (difference * -1) + average  # difference * -1  + average
            logging.info("Adjustment")
            logging.info(adjustment)
            _adjustment = bytearray(struct.pack('cd', b'@', adjustment))
            self.udp.send(_adjustment, dest=address)

    def average_calc(self):
        average = 0.0
        for _, difference in self.workers.items():
            average += difference
        try:
            return average / (len(self.workers)+1)
        except ZeroDivisionError:
            return 0.0

    def __del__(self):
        self._t.join()
        logging.debug('exiting')
