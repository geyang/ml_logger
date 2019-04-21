from collections import namedtuple
from typing import NamedTuple, Any


class LogOptions(NamedTuple):
    overwrite: bool = None
    write_mode: str = None


class LogEntry(NamedTuple):
    key: str
    data: Any
    type: str
    options: LogOptions = None


class LoadEntry(NamedTuple):
    key: str
    type: str
    start: Any = None
    stop: Any = None


RemoveEntry = namedtuple("RemoveEntry", ['key'])


class GlobEntry(NamedTuple):
    query: str
    wd: Any = None
    recursive: bool = True
    start: Any = None
    stop: Any = None


class PingData(NamedTuple):
    exp_key: str
    status: Any
    burn: bool = False


Signal = namedtuple("Signal", ['exp_key', 'signal'])

import numpy as np

ALLOWED_TYPES = (np.uint8,)  # ONLY uint8 is supported.
