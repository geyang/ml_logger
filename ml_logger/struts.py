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
    wd: str = "."
    recursive: bool = True
    start: Any = None
    stop: Any = None


class MoveEntry(NamedTuple):
    source: str
    to: str


class CopyEntry(NamedTuple):
    source: str
    to: str
    # for files
    exists_ok: bool
    follow_symlink: bool
    # for directories
    symlinks: bool


class PingData(NamedTuple):
    exp_key: str
    status: Any
    burn: bool = False


class MakeVideoEntry(NamedTuple):
    files: str
    key: str
    wd: str = "."
    order: str = None
    options: Any = None


Signal = namedtuple("Signal", ['exp_key', 'signal'])

import numpy as np

ALLOWED_TYPES = (np.uint8,)  # ONLY uint8 is supported.
