#-*- encoding: UTF-8 -*-
from threading import Timer

class CustomTimer:
    def __init__(self, value, f):
        self.timer = Timer(value, f)
        self.f = f

    def reset(self, value):
        if not self.timer.isAlive():
            raise CustomTimerException("don't reset when timer not started")
        self.timer.cancel()
        self.timer = Timer(value, self.f)
        self.timer.start()

    def start(self):
        if self.timer.isAlive():
            raise CustomTimerException("don't start a timer when he's already up")
        self.timer.start()

class CustomTimerException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
