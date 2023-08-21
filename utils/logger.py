import functools
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
    LOG_METHODS = {
        "back": ("debug", "light_cyan"),
        "note": ("info", "light_magenta"),
        "msg": ("info", "light_cyan"),
        "file": ("info", "light_blue"),
        "line": ("info", "light_blue"),
        "success": ("info", "light_green"),
        "warn": ("warning", "light_red"),
        "err": ("error", "red"),
    }
    INDENT_METHODS = [
        "indent",
        "set_indent",
        "reset_indent",
        "store_indent",
        "restore_indent",
        "log_indent",
    ]

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

        self.log_indent = 0
        self.log_indents = []

        self.bind_functions()

    def indent(self, indent=2):
        self.log_indent += indent

    def set_indent(self, indent=2):
        self.log_indent = indent

    def reset_indent(self):
        self.log_indent = 0

    def store_indent(self):
        self.log_indents.append(self.log_indent)

    def restore_indent(self):
        self.log_indent = self.log_indents.pop(-1)

    def log(self, method, msg, *args, **kwargs):
        level, color = self.LOG_METHODS[method]
        indent_str = " " * self.log_indent
        indented_msg = f"{indent_str}{msg}"
        getattr(self.logger, level)(colored(indented_msg, color), *args, **kwargs)

    def bind_functions(self):
        for method in self.LOG_METHODS:
            setattr(self.logger, method, functools.partial(self.log, method))

        for method in self.INDENT_METHODS:
            setattr(self.logger, method, getattr(self, method))


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
