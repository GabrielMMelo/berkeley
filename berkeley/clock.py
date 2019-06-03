import random
import time


class Clock:
    def __init__(self):
        self.error = random.randint(0, 30) * 1000
        self.current_time = lambda: time.time() * 1000.0

    def get_error(self):
        return self.error

    def get_clock(self):
        return self.current_time() + self.error

    def set_adjustment(self, adjustment):
        self.error += adjustment

    def get_date(self):
        return time.ctime((self.get_clock())/1000)

    def get_difference(self, time):
        return self.get_clock() - time
