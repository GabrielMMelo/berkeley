from log import LogBase

from clock import Clock

#TODO: support for multiple managers


class BerkeleyBase(LogBase):
    def __init__(self, udp):
        LogBase.__init__(self)
        self.clock = Clock()
        self.udp = udp
