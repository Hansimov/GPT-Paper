import inspect
import logging
import os
import shutil
import subprocess
from termcolor import colored


def add_fillers(text, filler="=", direction="both"):
    terminal_width = shutil.get_terminal_size().columns
    text = text.strip()
    text_width = len(text)
    if text_width >= terminal_width:
        return text

    if direction == "both":
        leading_fill_str = filler * ((terminal_width - text_width) // 2 - 1) + " "
        trailing_fill_str = " " + filler * (
            terminal_width - text_width - len(leading_fill_str) - 1
        )
    elif direction == "left":
        leading_fill_str = filler * (terminal_width - text_width - 1) + " "
        trailing_fill_str = ""
    elif direction == "right":
        leading_fill_str = ""
        trailing_fill_str = " " + filler * (terminal_width - text_width - 1)
    else:
        raise ValueError("Invalid direction")

    filled_str = f"{leading_fill_str}{text}{trailing_fill_str}"
    return filled_str


class Logger:
    def __init__(self, name=None, prefix=False):
        if not name:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            name = module.__name__

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if prefix:
            formatter_prefix = "[%(asctime)s] - [%(name)s] - [%(levelname)s]\n"
        else:
            formatter_prefix = ""

        self.formatter = logging.Formatter(formatter_prefix + "%(message)s")

        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.INFO)

        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        self.bind_functions()

    def note(self, msg, *args, **kwargs):
        self.logger.info(colored(msg, "light_cyan"), *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        self.logger.info(colored(msg, "light_green"), *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.logger.warning(colored(msg, "light_magenta"), *args, **kwargs)

    def err(self, msg, *args, **kwargs):
        self.logger.error(colored(msg, "light_red"), *args, **kwargs)

    def bind_functions(self):
        self.logger.note = self.note
        self.logger.success = self.success
        self.logger.warn = self.warn
        self.logger.err = self.err


logger = Logger().logger


def shell_cmd(cmd, getoutput=False, showcmd=True):
    if showcmd:
        logger.info(colored(f"\n$ [{os.getcwd()}]", "light_blue"))
        logger.info(colored(f"  $ {cmd}\n", "light_cyan"))
    if getoutput:
        output = subprocess.getoutput(cmd)
        return output
    else:
        subprocess.run(cmd, shell=True)
