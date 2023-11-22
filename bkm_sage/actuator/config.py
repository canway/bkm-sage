import logging
from datetime import datetime
from operator import le

import click

logging.getLogger()


class ClickLogger:
    def __init__(self):
        self.embedded_prefix = "..."

    def debug(self, msg, *args, **kwargs):
        self.log(logging.DEBUG, msg)

    def info(self, msg, *args, **kwargs):
        self.log(logging.INFO, msg)

    def warn(self, msg, *args, **kwargs):
        self.log(logging.WARN, msg)

    def error(self, msg, *args, **kwargs):
        self.log(logging.ERROR, msg)

    def success(self, msg, *arg, **kwargs):
        self.log(logging.INFO, msg, fg="green")

    def log(self, level: int, msg: str, fg: str = None):
        fg_mapping = {
            logging.DEBUG: None,
            logging.INFO: None,
            logging.WARN: "yellow",
            logging.ERROR: "red",
        }
        fg = fg if fg else fg_mapping[level]
        message = "{prefix} {t} [{level}] {msg}".format(
            prefix=self.embedded_prefix,
            t=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            level=logging.getLevelName(level),
            msg=msg,
        )
        click.secho(message, fg=fg)

    def enter(self):
        click.echo("\n")


class Config:
    logger = ClickLogger()
    save_action_messages = True


default_config = Config()
