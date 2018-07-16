import os

from params_proto import cli_parse, Proto


@cli_parse
class Args:
    logdir = os.path.realpath(".")


@cli_parse
class ServerArgs:
    host = Proto("", help="use 0.0.0.0 if you want external clients to be able to access this.")
    port = 8082
    workers = 1
    debug = False
