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


LoadEntry = namedtuple("LoadEntry", ['key', 'type'])
RemoveEntry = namedtuple("RemoveEntry", ['key'])


class PingData(NamedTuple):
    exp_key: str
    status: Any
    burn: bool = False


Signal = namedtuple("Signal", ['exp_key', 'signal'])

import numpy as np

ALLOWED_TYPES = (np.uint8,)  # ONLY uint8 is supported.
