import os

from params_proto import cli_parse


@cli_parse
class Args:
    logdir = os.path.realpath(".")

@cli_parse
class ServerArgs:
    host = ""
    port = 8082
    workers = 1
    debug = False
