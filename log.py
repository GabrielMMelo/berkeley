import logging
import sys


class LogBase:
    class Log:
        def __init__(self, name):
            self.log = logging.getLogger(name)
            self.handler = logging.StreamHandler(stream=sys.stdout)  # console stream
            self.handler.setLevel(logging.INFO)
            self.c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            self.handler.setFormatter(self.c_format)
            self.log.addHandler(self.c_format)

        def set_name(self, name):
            self.log = logging.getlog(name)

        def info(self, msg):
            self.log.info(msg)

        def debug(self, msg):
            self.log.debug(msg)

        def warning(self, msg):
            self.log.warning(msg)

        def error(self, msg):
            self.log.error(msg)

    def __init__(self, name=__name__):
        self.logger = self.Log(name)
