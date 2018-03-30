import logging
import sys
import os


class Logger:
    def __init__(self, logName, logFile):
        self._logger = logging.getLogger(logName)

        log_dir = "./log"
        if os.path.exists(log_dir) == False:
            os.mkdir(log_dir)

        log_filename = log_dir + '/' + logFile

        handler = logging.FileHandler(log_filename)
        formatter = logging.Formatter(
            '%(asctime)s %(funcName)s [line:%(lineno)d]  %(levelno)s %(levelname)s  threadID:%(thread)d threadName:%(threadName)s msg:%(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def info(self, msg):
        if self._logger is not None:
            self._logger.info(msg)