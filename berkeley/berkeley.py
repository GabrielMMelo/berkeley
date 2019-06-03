import logging as log
import sys

from berkeley.clock import Clock

log.basicConfig(stream=sys.stdout, level=log.DEBUG)


class BerkeleyBase:
    def __init__(self, udp):
        self.clock = Clock()
        self.udp = udp
        log.info("Initial error (ms):")
        log.info(self.clock.get_error())
