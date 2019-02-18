import os

from params_proto import cli_parse, Proto


@cli_parse
class Args:
    logdir = Proto(os.path.realpath("."), help="the root directory for all of the logs")


@cli_parse
class ServerArgs:
    host = Proto("", help="use 0.0.0.0 if you want external clients to be able to access this.")
    port = Proto(8081, help="the port")
    workers = Proto(1, help="the number of worker processes")
    debug = False
