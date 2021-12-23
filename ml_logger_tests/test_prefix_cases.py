import os

"""
Details of the logging prefix

root = $PWD, prefix = "" -> log to $PWD locally.
                         -> log to server $LOGDIR remotely.
root = $PWD, prefix = "/" -> log to "/" locally.
                          -> log to server $LOGDIR remotely. (removes the '/')
logger client contains thread pools, should not be re-created lightly.
"""


def test_local_relative():
    root = "/"
    cwd = "/cwd"
    prefix = "wat"
    log_dir = os.path.join(cwd, prefix)
    assert os.path.join(root, log_dir[1:]) == "/cwd/wat"


def test_local_absolute():
    root = "/"
    cwd = "/cwd"
    prefix = "/wat"
    log_dir = os.path.join(cwd, prefix)
    assert os.path.join(root, log_dir[1:]) == "/wat"


def test_server_relative():
    root = "/data_dir"
    cwd = "/"
    prefix = "wat"
    log_dir = os.path.join(cwd, prefix)
    assert os.path.join(root, log_dir[1:]) == "/data_dir/wat"


def test_server_absolute():
    root = "/data_dir"
    cwd = "/"
    prefix = "/wat"
    log_dir = os.path.join(cwd, prefix)
    assert os.path.join(root, log_dir[1:]) == "/data_dir/wat"


def test_server_system_absolute():
    root = "/"
    cwd = "/"
    prefix = "//wat"
    log_dir = os.path.join(cwd, prefix)
    assert os.path.join(root, log_dir[1:]) == "/wat"
