import inspect
import logging
from termcolor import colored


class Logger:
    def __init__(self, name=None):
        if not name:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            name = module.__name__

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        self.formatter = logging.Formatter(
            "[%(asctime)s] - [%(name)s] - [%(levelname)s]\n%(message)s"
        )

        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.INFO)

        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
