import time
import threading
import struct

from .berkeley import BerkeleyBase

WORKERS_LIMIT = 2
RETRANSMISSION_INTERVAL = 5


class Manager(BerkeleyBase):
    def __init__(self, udp):
        BerkeleyBase.__init__(self, udp)
        self.udp.bind()
        self.workers = {}
        self._t = threading.Thread(target=self.receive_workers)
        self._t.start()
        self.loop()

    def loop(self):
        while True:
            print("TIME:", self.clock.get_clock())
            print("DATE:", self.clock.get_date())
            self.logger.debug('broadcasting...')
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
        # TODO: Pensar melhor o limite daqui
        while len(self.workers) <= WORKERS_LIMIT:
            _data, address = self.udp.recv()
            if _data == b'#':
                self.logger.info("New worker!")
                self.logger.info(address)
                self.workers[address] = 0
            else:
                data = struct.unpack('d', _data)[0]
                self.workers[address] = data  # refresh difference
        self.logger.debug('leave receive_workers')

    def update_clocks(self):
        average = self.average_calc()
        self.logger.info("Average")
        self.logger.info(average)
        self.clock.set_adjustment(average)  # update manager clock
        for address, difference in self.workers.items():
            adjustment = (difference * -1) + average  # difference * -1  + average
            self.logger.info("Adjustment")
            self.logger.info(adjustment)
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
        self.logger.debug('exiting')
