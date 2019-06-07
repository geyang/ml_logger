import os

from params_proto import cli_parse


@cli_parse
class Args:
    logdir = os.path.realpath(".")
    port = 8082
