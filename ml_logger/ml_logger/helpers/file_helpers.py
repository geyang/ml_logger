import os

from contextlib import contextmanager


@contextmanager
def CwdContext(path):
    owd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(owd)
