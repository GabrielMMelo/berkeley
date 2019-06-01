import sys

from berkeley import Berkeley
from udp import Udp

host = sys.argv[1]
port = int(sys.argv[2])
is_manager = False if int(sys.argv[3]) == 0 else True

udp = Udp(host, port)
berkeley = Berkeley(udp, is_manager)
