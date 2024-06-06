import logging
import os
from termcolor import colored
from datetime import datetime
import pytz
import time

class ColouredLogger(logging.Logger):
    def __init__(self, name):
        super(ColouredLogger, self).__init__(name)
        self.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(funcName)20s() - %(levelname)s - %(message)s')
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(self.formatter)
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist).strftime("%Y%m-%d%H-%M%S")
        self.fh = logging.FileHandler(f'audiosocket_{now}.log')
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.formatter)
        self.addHandler(self.ch)
        self.addHandler(self.fh)

    def debug(self, msg):
        # Get the filename and line number of the error
        frame = logging.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        # Append the filename and line number to the message
        msg = f'{msg} - File: {filename}, Line: {lineno}'
        super(ColouredLogger, self).debug(colored(msg, 'blue'))

    def info(self, msg):
        # Get the filename and line number of the error
        frame = logging.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        # Append the filename and line number to the message
        msg = f'{msg} - File: {filename}, Line: {lineno}'
        super(ColouredLogger, self).info(colored(msg, 'green'))

    def warning(self, msg):
        # Get the filename and line number of the error
        frame = logging.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        # Append the filename and line number to the message
        msg = f'{msg} - File: {filename}, Line: {lineno}'
        super(ColouredLogger, self).warning(colored(msg, 'yellow'))

    def error(self, msg):
        # Get the filename and line number of the error
        frame = logging.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        # Append the filename and line number to the error message
        error_msg = f'{msg} - File: {filename}, Line: {lineno}'
        super(ColouredLogger, self).error(colored(error_msg, 'red'))

    def critical(self, msg):
        # Get the filename and line number of the error
        frame = logging.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        # Append the filename and line number to the error message
        error_msg = f'{msg} - File: {filename}, Line: {lineno}'
        super(ColouredLogger, self).critical(colored(error_msg, 'red', 'on_white'))