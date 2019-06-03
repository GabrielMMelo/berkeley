import sys

from berkeley.manager import Manager
from berkeley.worker import Worker
from udp.udp import Udp

host = sys.argv[1]
port = int(sys.argv[2])
is_manager = False if int(sys.argv[3]) == 0 else True

udp = Udp(host, port)
if is_manager:
    manager = Manager(udp)
else:
    worker = Worker(udp)
