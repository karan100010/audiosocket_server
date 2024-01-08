#create a colourd logger class that can be used to log messages to the console and to a file
import logging
from termcolor import colored

class ColouredLogger(logging.Logger):
    def __init__(self, name):
        super(ColouredLogger, self).__init__(name)
        self.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(funcName)20s() - %(levelname)s - %(message)s')
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(self.formatter)
        self.fh = logging.FileHandler('audiosocket.log')
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.formatter)
        self.addHandler(self.ch)
        self.addHandler(self.fh)

    def debug(self, msg):
        super(ColouredLogger, self).debug(colored(msg, 'blue'))

    def info(self, msg):
        super(ColouredLogger, self).info(colored(msg, 'green'))

    def warning(self, msg):
        super(ColouredLogger, self).warning(colored(msg, 'yellow'))

    def error(self, msg):
        super(ColouredLogger, self).error(colored(msg, 'red'))

    def critical(self, msg):
        super(ColouredLogger, self).critical(colored(msg, 'red', 'on_white'))