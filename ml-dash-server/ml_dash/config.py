import os

from params_proto import cli_parse, Proto


@cli_parse
class Args:
    """
    ML-Dash
    -------

    This module contains `ml_dash.server`, the visualization backend, and `ml_dash.app`, a
    static server hosting the web application.

    Usage
    -----

        python -m ml_dash.server --port 8090 --host 0.0.0.0 --workers 10

    """
    logdir = Proto(os.path.realpath("."), help="the root directory for all of the logs")


@cli_parse
class ServerArgs:
    host = Proto("", help="use 0.0.0.0 if you want external clients to be able to access this.")
    port = Proto(8081, help="the port")
    workers = Proto(1, help="the number of worker processes")
    debug = False

@cli_parse
class SSLArgs:
    cert = Proto(None, dtype=str, help="the path to the SSL certificate")
    key = Proto(None, dtype=str, help="the path to the SSL key")
