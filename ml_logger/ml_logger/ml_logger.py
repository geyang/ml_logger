from collections import defaultdict

import numpy as np
import os
from collections.abc import Sequence
from contextlib import contextmanager
from functools import partial
from io import BytesIO
from math import ceil
from ml_logger.helpers import load_from_pickle_file, load_from_jsonl_file
from numbers import Number
from random import random
from termcolor import cprint
from time import perf_counter, sleep
from typing import Any, Union
from typing import NamedTuple
from waterbear import DefaultBear

from .caches.key_value_cache import KeyValueCache
from .caches.summary_cache import SummaryCache
from .full_duplex import Duplex
from .helpers.color_helpers import Color
from .helpers.default_set import DefaultSet
from .helpers.print_utils import PrintHelper
from .log_client import LogClient

# environment defaults
CWD = os.environ["PWD"]
USER = os.environ["USER"]

# ML_Logger defaults
ROOT = os.environ.get("ML_LOGGER_ROOT", CWD) or CWD
USER = os.environ.get("ML_LOGGER_USER", USER)
ACCESS_TOKEN = os.environ.get("ML_LOGGER_ACCESS_TOKEN", None)


def pJoin(*args):
    from os.path import join
    args = [a for a in args if a]
    if args:
        return join(*args)
    return None


def now(fmt=None):
    """
    This is not idempotent--each call returns a new value. So it has to be a method

    returns a datetime object if no format string is specified.
    Otherwise returns a formated string.

    Each call returns the current time.

    :param fmt: formating string, i.e. "%Y-%m-%d-%H-%M-%S-%f"
    :return: OneOf[datetime, string]
    """
    # todo: add time zone support
    from datetime import datetime
    now = datetime.now().astimezone()
    return now.strftime(fmt) if fmt else now


# todo: move to analysis
class BinOptions(NamedTuple):
    key: str
    n: int = None
    size: int = None


def metrify(data):
    """Help convert non-json serializable objects, such as

    :param data:
    :return:
    """
    if hasattr(data, 'shape') and len(data.shape) > 0:
        return list(data)
    elif isinstance(data, Sequence):
        return data
    elif isinstance(data, Number):
        return data
    elif data is None:
        return data
    elif type(data) in [dict, str, bool, str]:
        return data
    # todo: add datetime support
    elif not hasattr(data, 'dtype'):
        return str(data)
    elif str(data.dtype).startswith('int'):
        return int(data)
    elif str(data.dtype).startswith('float'):
        return float(data)
    else:
        return str(data)


ML_DASH = "http://localhost:3001/{prefix}"


@contextmanager
def _PrefixContext(logger, new_prefix=None, metrics=None, sep="/"):
    old_metrics_prefix = logger.metrics_prefix
    old_prefix = logger.prefix

    sep = sep or ""

    if new_prefix:
        logger.prefix = new_prefix + sep
    if metrics:
        logger.metrics_prefix = metrics + sep
    elif metrics is False:
        logger.metrics_prefix = ""
    try:
        yield
    finally:
        logger.prefix = old_prefix
        logger.metrics_prefix = old_metrics_prefix


# @contextmanager
# def _LocalContext(logger, new_prefix=None):
#     old_client = logger.client
#     logger.prefix = new_prefix
#     try:
#         yield
#     finally:
#         logger.prefix = old_prefix

def interpolate(path=None):
    if path is None:
        return None
    path = str(path)
    if path.startswith("$"):
        return os.environ.get(path[1:], None)
    return path


# noinspection PyPep8Naming
class ML_Logger:
    """
    ML_Logger, a logging utility for ML training.
    ---
    """
    client = None
    root_dir = None

    prefix = ""  # is okay b/c strings are immutable in python
    metrics_prefix = ""
    print_buffer = None  # move initialization to init.
    print_buffer_size = 2048

    ### Context Helpers
    def Prefix(self, *praefixa, metrics=None, sep="/"):
        """
        Returns a context in which the prefix of the logger is set to `prefix`
        :param praefixa: the new prefix
        :return: context object
        """
        try:
            path_prefix = os.path.normpath(pJoin(self.prefix, *praefixa))
            return _PrefixContext(self, path_prefix, metrics, sep=sep)
        except:
            return _PrefixContext(self, metrics=metrics, sep=sep)

    def Sync(self, clean=False, **kwargs):
        """
        Returns a context in which the logger logs synchronously. The new
        synchronous request pool is cached on the logging client, so this
        context can happen repetitively without creating a run-away number
        of parallel threads.

        The context object can only be used once b/c it is create through
        generator using the @contextmanager decorator.

        :param clean: boolean flag for removing the thead pool after __exit__.
            used to enforce single-use SyncContexts.
        :param max_workers: `urllib3` session pool `max_workers` field
        :return: context object
        """
        return self.client.SyncContext(clean=clean, **kwargs)

    def Async(self, clean=False, **kwargs):
        """
        Returns a context in which the logger logs [a]synchronously. The new
        asynchronous request pool is cached on the logging client, so this
        context can happen repetitively without creating a run-away number
        of parallel threads.

        The context object can only be used once b/c it is create through
        generator using the @contextmanager decorator.

        :param clean: boolean flag for removing the thead pool after __exit__.
            used to enforce single-use AsyncContexts.
        :param max_workers: `future_sessions.Session` pool `max_workers` field
        :return: context object
        """
        return self.client.AsyncContext(clean=clean, **kwargs)

    PrefixContext = Prefix
    SyncContext = Sync
    AsyncContext = Async

    def __repr__(self):
        return f'Logger(log_directory="{self.root_dir}",' + "\n" + \
               f'       prefix="{self.prefix}")'

    # noinspection PyInitNewSignature
    # todo: use prefixes as opposed to prefix. (add *prefixae after prefix=None)
    # todo: resolve path segment with $env variables.
    def __init__(self, prefix="", *prefixae,
                 log_dir=ROOT, user=USER, access_token=ACCESS_TOKEN,
                 buffer_size=2048, max_workers=None,
                 asynchronous=None, summary_cache_opts: dict = None):
        """ logger constructor.

        Assumes that you are starting from scratch.

        | `log_directory` is overloaded to use either
        | 1. file://some_abs_dir
        | 2. http://19.2.34.3:8081
        | 3. /tmp/some_dir
        |
        | `prefix` is the log directory relative to the root folder. Absolute path are resolved against the root.
        | 1. prefix="causal_infogan" => logs to "/tmp/some_dir/causal_infogan"
        | 2. prefix="" => logs to "/tmp/some_dir"

        :param prefix: the prefix path
        :param **prefixae: the rest of the prefix arguments
        :param log_dir: the server host and port number
        :param user: environment $ML_LOGGER_USER
        :param access_token: environment $ML_LOGGER_ACCESS_TOKEN
        :param asynchronous: When this is not None, we create a http thread pool.
        :param buffer_size: The string buffer size for the print buffer.
        :param max_workers: the number of request-session workers for the async http requests.
        """
        # self.summary_writer = tf.summary.FileWriter(log_directory)
        self.step = None
        self.duplex = None
        self.timestamp = None

        self.do_not_print = DefaultSet("__timestamp")
        self.print_helper = PrintHelper()

        # init print buffer
        self.print_buffer_size = buffer_size
        self.print_buffer = ""

        self.timer_cache = defaultdict(None)
        self.key_value_caches = defaultdict(KeyValueCache)
        self.summary_caches = defaultdict(partial(SummaryCache, **(summary_cache_opts or {})))

        # todo: add https support
        self.root_dir = interpolate(log_dir) or ROOT

        prefixae = [interpolate(p) for p in (prefix or "", *prefixae) if p is not None]
        self.prefix = os.path.join(*prefixae) if prefixae else ""
        self.client = LogClient(root=self.root_dir, user=user, access_token=access_token,
                                asynchronous=asynchronous, max_workers=max_workers)

    def configure(self,
                  prefix=None,
                  *prefixae,
                  log_dir: str = None,
                  user=None,
                  access_token=None,
                  asynchronous=None,
                  max_workers=None,
                  buffer_size=None,
                  summary_cache_opts: dict = None,
                  register_experiment=True,
                  silent=False,
                  ):
        """
        Configure an existing logger with updated configurations.

        # LogClient Behavior

        The logger.client would be re-constructed if

            - root_dir is changed
            - max_workers is not None
            - asynchronous is not None

        Because the http LogClient contains http thread pools, one shouldn't call this
        configure function in a loop. Instead, use the logger.(A)syncContext() contexts.
        That context caches the pool so that you don't create new thread pools again and
        again.

        # Cache Behavior

        Both key-value cache and the summary cache would be cleared if summary_cache_opts
        is set to not None. A new summary cache would be created, whereas the old
        key-value cache would be cleared.

        # Print Buffer Behavior
        If configure is called with a buffer_size not None, the old print buffer would
        be cleared.

        todo: I'm considering also clearing this buffer also when summary-cache is updated.
        The use-case of changing print_buffer_size is pretty small. Should probaly
        just deprecate this.

        # Registering New Experiment

        This is a convinient default for new users. It prints out a dashboard link to
        the dashboard url.

        todo: the table at the moment seems a bit verbose. I'm considering making this
          just a single line print.

        :param prefix: the first prefix
        :param *prefixae: a list of prefix segments
        :param log_dir:
        :param user:
        :param access_token:
        :param buffer_size:
        :param summary_cache_opts:
        :param asynchronous:
        :param max_workers:
        :param register_experiment:
        :param silent: bool, True to turn off the print.
        :return:
        """

        # path logic
        log_dir = interpolate(log_dir) or os.getcwd()
        if prefix is not None:
            prefixae = [interpolate(p) for p in (prefix, *prefixae) if p is not None]
            if prefixae is not None:
                self.prefix = os.path.join(*prefixae)

        if buffer_size is not None:
            self.print_buffer_size = buffer_size
            self.print_buffer = ""

        if summary_cache_opts is not None:
            self.key_value_caches.clear()
            self.summary_caches.clear()
            self.summary_caches = defaultdict(partial(SummaryCache, **(summary_cache_opts or {})))

        if log_dir:
            self.root_dir = interpolate(log_dir) or ROOT
        if log_dir or asynchronous is not None or max_workers is not None:
            # note: logger.configure shouldn't be called too often. To quickly switch back
            #  and forth between synchronous and asynchronous calls, use the `SyncContext`
            #  and `AsyncContext` instead.
            if not silent:
                cprint('creating new logging client...', color='yellow', end='\r')
            self.client.__init__(root=self.root_dir, user=user, access_token=access_token,
                                 asynchronous=asynchronous, max_workers=max_workers)
            if not silent:
                cprint('✓ created a new logging client', color="green")

        if not silent:
            from urllib.parse import quote
            print(f"Dashboard: {ML_DASH.format(prefix=quote(self.prefix))}")
            print(f"Log_directory: {self.root_dir}")

        # now register the experiment
        if register_experiment:
            with logger.SyncContext(clean=True):  # single use SyncContext
                self.log_params(run=self.run_info(), silent=silent)

    def run_info(self, **kwargs):
        return {
            "createTime": self.now(),
            "prefix": self.prefix,
            **kwargs
        }

    @staticmethod
    def fn_info(fn):
        """
        logs information of the caller's stack (module, filename etc)

        :param fn:
        :return: info = dict(
                            name=_['__name__'],
                            doc=_['__doc__'],
                            module=_['__module__'],
                            file=_['__globals__']['__file__']
                            )
        """
        from functools import partial
        from inspect import getmembers

        while True:
            if hasattr(fn, "__wrapped__"):
                fn = fn.__wrapped__
            elif isinstance(fn, partial):
                fn = fn.func
            else:
                break

        _ = dict(getmembers(fn))
        doc_string = _['__doc__']
        if doc_string and len(doc_string) > 46:
            doc_string = doc_string[:46] + " ..."
        info = dict(name=_['__name__'], doc=doc_string, module=_['__module__'],
                    file=_['__globals__']['__file__'])
        return info

    def rev_info(self):
        return dict(hash=self.__head__, branch=self.__current_branch__)

    counter = DefaultBear(lambda: 0)

    def every(self, n=1, key="default"):
        """
        returns True every n counts. Use the key to count different intervals.

        Example:

        .. code:: python

            for i in range(100):
                if logger.every(10):
                    print('every tenth count!')
                if logger.every(100, "hudred"):
                    print('every 100th count!')

        :param n:
        :param key:
        :return:
        """
        self.counter[key] += 1
        return n and self.counter[key] % n == 0

    def count(self, key="default"):
        self.counter[key] += 1
        return self.counter[key]

    def clear(self, key="default"):
        try:
            del self.counter[key]
        except KeyError:
            pass

    def start(self, *keys):
        """
        starts a timer, saved in float in seconds.

        Automatically de-dupes the keys, but will return the same
        number of intervals. duplicates will recieve the same
        result.

        .. code:: python

            from ml_logger import logger

            logger.start('loop', 'iter')
            it = 0
            for i in range(10):
                it += logger.split('iter')
            print('iteration', it / 10)
            print('loop', logger.since('loop'))

        :param *keys: position arguments are timed together.
        :return: float (in seconds)
        """
        keys = keys or ['default']
        results = {k: None for k in keys}
        new_tic = self.now()
        for key in set(keys):
            self.timer_cache[key] = new_tic

        return results[keys[0]] \
            if len(keys) == 1 else [results[k] for k in keys]

    def since(self, *keys):
        """
        returns a float in seconds when 1 key is passed, or
        a list of floats when multiple keys are passsed in.

        Automatically de-dupes the keys, but will return the same
        number of intervals. duplicates will recieve the same
        result.

        Note: This *is* idempotent.

        .. code:: python

            from ml_logger import logger

            logger.start('loop', 'iter')
            it = 0
            for i in range(10):
                it += logger.split('iter')
            print('iteration', it / 10)
            print('loop', logger.since('loop'))

        :param *keys: position arguments are timed together.
        :return: float (in seconds)
        """
        keys = keys or ['default']
        results = {k: None for k in keys}
        tick = self.now()
        for key in set(keys):
            try:
                dt = tick - self.timer_cache[key]
                results[key] = dt.total_seconds()
            except:
                # not sure if setting an empty cache is good
                self.timer_cache[key] = tick
                results[key] = None

        return results[keys[0]] \
            if len(keys) == 1 else [results[k] for k in keys]

    # timing functions
    def split(self, *keys):
        """
        returns a float in seconds when 1 key is passed, or
        a list of floats when multiple keys are passsed in.

        Automatically de-dupes the keys, but will return the same
        number of intervals. duplicates will recieve the same
        result.

        Note: This is Not idempotent, which is why it is not a property.

        .. code:: python

            from ml_logger import logger

            logger.split('loop', 'iter')
            it = 0
            for i in range(10):
                it += logger.split('iter')
            print('iteration', it / 10)
            print('loop', logger.split('loop'))

        :param *keys: position arguments are timed together.
        :return: float (in seconds)
        """
        keys = keys or ['default']
        results = {k: None for k in keys}
        new_tic = perf_counter()
        for key in set(keys):
            try:
                results[key] = new_tic - self.timer_cache[key]
            except:
                pass
            self.timer_cache[key] = new_tic

        return results[keys[0]] if len(keys) == 1 else [results[k] for k in keys]

    @contextmanager
    def time(self, key="default", interval=1):
        key, original = f"time.{key}", key
        self.split(key)
        yield
        delta = self.split(key)
        self.store(delta=delta, cache=key)
        if self.every(interval, key=key):
            logger.print(f"timing <{original}>:", end=" ")
            data = self.summary_caches[key]['delta']
            if interval > 1:
                logger.print(f"{data.mean():0.3E}s", color="green", end=" ")
                logger.print(f"±{data.std():0.1E}")
            else:
                logger.print(f"{data.mean():0.3E}s", color="green")

    @staticmethod
    def now(fmt=None):
        return now(fmt)

    def truncate(self, path, depth=-1):
        """
        truncates the path's parent directories w.r.t. given depth. By default, returns the filename
        of the path.

        .. code:: python

            path = "/Users/geyang/some-proj/experiments/rope-cnn.py"
            logger.truncate(path, -1)

        ::

            "rope-cnn.py"

        .. code:: python

            logger.truncate(path, 4)

        ::

            "experiments/rope-cnn.py"

        This is useful for saving the *relative* path of your main script.

        :param path: "learning-to-learn/experiments/run.py"
        :param depth: 1, 2... when 1 it picks only the file name.
        :return: "run"
        """
        return "/".join(path.split('/')[depth:])

    def stem(self, path):
        """
        returns the stem of the filename in the path, truncates parent directories w.r.t. given depth.

        .. code:: python

            path = "/Users/geyang/some-proj/experiments/rope-cnn.py"
            logger.stem(path)

        ::

            "/Users/geyang/some-proj/experiments/rope-cnn"

        You can use this in combination with the truncate function.
        .. code:: python

            _ = logger.truncate(path, 4)
            _ = logger.stem(_)

        ::

            "experiments/rope-cnn"

        This is useful for saving the *relative* path of your main script.

        :param path: "learning-to-learn/experiments/run.py"
        :return: "run"
        """
        return os.path.splitext(path)[0]

    def diff(self, diff_directory=".", diff_filename="index.diff", ref="HEAD", verbose=False):
        """
        example usage:

        .. code:: python

            from ml_logger import logger

            logger.diff()  # => this writes a diff file to the root of your logging directory.

        :param ref: the ref w.r.t which you want to diff against. Default to HEAD
        :param diff_directory: The root directory to call `git diff`, default to current directory.
        :param diff_filename: The file key for saving the diff file.
        :param verbose: if True, print out the command.

        :return: string containing the content of the patch
        """
        import subprocess
        try:
            cmd = f'cd "{os.path.realpath(diff_directory)}" && git diff {ref} --binary'
            if verbose: self.log_line(cmd)
            p = subprocess.check_output(cmd, shell=True)  # Save git diff to experiment directory
            patch = p.decode('utf-8').strip()
            self.log_text(patch, diff_filename)
            return patch
        except subprocess.CalledProcessError as e:
            self.log_line("not storing the git diff due to {}".format(e))

    @property
    def __status__(self):
        """
        example usage:
        --------------

        .. code:: python

            from ml_logger import logger

            diff = logger.__status__  # => this writes a diff file to the root of your logging directory.

        :return: the diff string for the current git repo.
        """
        import subprocess
        try:
            cmd = f'cd "{os.path.getcwd()}" && git status -vv'
            p = subprocess.check_output(cmd, shell=True)  # Save git diff to experiment directory
            return p.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            return e

    @property
    def __current_branch__(self):
        import subprocess
        try:
            cmd = f'git symbolic-ref HEAD'
            p = subprocess.check_output(cmd, shell=True)  # Save git diff to experiment directory
            return p.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return None

    @property
    def __head__(self):
        """returns the git revision hash of the head if inside a git repository"""
        return self.git_rev('HEAD')

    def git_rev(self, branch):
        """
        Helper function **used by `logger.__head__`** that returns the git revision hash of the
        branch that you pass in.

        full reference here: https://stackoverflow.com/a/949391
        the `show-ref` and the `for-each-ref` commands both show a list of refs. We only need to get the
        ref hash for the revision, not the entire branch of by tag.
        """
        import subprocess
        try:
            cmd = ['git', 'rev-parse', branch]
            p = subprocess.check_output(cmd)
            return p.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return None

    @property
    def __tags__(self):
        return self.git_tags()

    def git_tags(self):
        import subprocess
        try:
            cmd = ["git", "describe", "--tags"]
            p = subprocess.check_output(cmd)  # Save git diff to experiment directory
            return p.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return None

    def diff_file(self, path, silent=False):
        raise NotImplementedError

    @property
    def job_id(self):
        import os
        return os.getenv("SLURM_JOB_ID", None)

    @property
    def hostname(self):
        import subprocess
        cmd = 'hostname -f'
        try:
            p = subprocess.check_output(cmd, shell=True)  # Save git diff to experiment directory
            return p.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            self.log_line(f"can not get obtain hostname via `{cmd}` due to exception: {e}")
            return None

    def ping(self, status='running', interval=None):
        """
        pings the instrumentation server to stay alive. Gets a control signal in return.
        The background thread is responsible for making the call . This method just returns the buffered
        signal synchronously.

        :return: tuple signals
        """
        if not self.duplex:
            def thunk(*statuses):
                nonlocal self
                if len(statuses) > 0:
                    return self.client.ping(self.prefix, statuses[-1])
                else:
                    return self.client.ping(self.prefix, "running")

            self.duplex = Duplex(thunk, interval or 120)  # default interval is two minutes
            self.duplex.start()
        if interval:
            self.duplex.keep_alive_interval = interval

        buffer = self.duplex.read_buffer()
        self.duplex.send(status)
        return buffer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # todo: wait for logger to finish upload in async mode.
        self.flush()

    def remove(self, path):
        """
        removes files and folders by path

        :param path:
        :return:
        """
        paths = self.glob(path, wd=None) if "*" in path else [path]
        for p in paths or []:
            abs_path = pJoin(self.prefix, p)
            self.client.delete(abs_path)

    def log_params(self, path="parameters.pkl", silent=False, **kwargs):
        """
        Log namespaced parameters in a list.

        Examples:

        .. code:: python

            logger.log_params(some_namespace=dict(layer=10, learning_rate=0.0001))

        generates a table that looks like:

        ::

            ══════════════════════════════════════════
               some_namespace
            ────────────────────┬─────────────────────
                   layer        │ 10
               learning_rate    │ 0.0001
            ════════════════════╧═════════════════════

        :param path: the file to which we save these parameters
        :param silent: do not print out
        :param kwargs: list of key/value pairs, each key representing the name of the namespace,
                       and the namespace itself.
        :return: None
        """
        from termcolor import colored as c
        key_width = 20
        value_width = 20

        _kwargs = {}
        table = []
        for n, (title, section_data) in enumerate(kwargs.items()):
            table.append('═' * (key_width) + ('═' if n == 0 else '╧') + '═' * (value_width + 1))
            table.append(c('{:^{}}'.format(title, key_width), 'yellow') + "")
            table.append('─' * (key_width) + "┬" + '─' * (value_width + 1))
            if not hasattr(section_data, 'items'):
                table.append(section_data)
                _kwargs[title] = metrify(section_data)
            else:
                _param_dict = {}
                for key, value in section_data.items():
                    _param_dict[key] = metrify(value.v if type(value) is Color else value)
                    value_string = str(value)
                    table.append('{:^{}}'.format(key, key_width) + "│ " + '{:<{}}'.format(value_string, value_width))
                _kwargs[title] = _param_dict

        if "n" in locals():
            table.append('═' * (key_width) + '╧' + '═' * (value_width + 1))

        # todo: add logging hook
        # todo: add yml support
        if table:
            (self.log_line if silent else self.print)(*table, sep="\n")
        self.log_data(path=path, data=_kwargs)

    def save_pkl(self, data, path=None, append=False, use_dill=False):
        """Save data in pkl format

        Note: We use dill so that we can save lambda functions but, but we use pure
            pickle when saving nn.Modules

        :param data: python data object to be saved
        :param path: path for the object, relative to the root logging directory.
        :param append: default to False -- overwrite by default
        :return: None
        """
        if use_dill:
            import dill as pickle
        else:
            import pickle

        path = path or "data.pkl"
        abs_path = pJoin(self.prefix, path)

        buf = BytesIO()

        pickle.dump(data, buf)
        buf.seek(0)
        self.client.log_buffer(abs_path, buf=buf.read(), overwrite=not append)
        return path

    def log_data(self, data, path=None, overwrite=False):
        """
        Append data to the file located at the path specified.

        :param data: python data object to be saved
        :param path: path for the object, relative to the root logging directory.
        :param overwrite: boolean flag to switch between 'appending' mode and 'overwrite' mode.
        :return: None
        """
        return self.save_pkl(data, path, append=not overwrite)

    def log_metrics(self, metrics=None, silent=None,
                    _prefix=None,
                    cache: Union[str, None] = None, file: Union[str, None] = None,
                    flush=None, **_key_values) -> None:
        """

        :param metrics: (mapping) key/values of metrics to be logged. Overwrites previous value if exist.
        :param silent: adds the keys being logged to the silent list, do not print out in table when flushing.
        :param cache: optional KeyValueCache object to be passed in
        :param flush:
        :param _key_values:
        :return:
        """
        cache_key = cache
        cache = self.key_value_caches[cache]
        timestamp = np.datetime64(self.now())

        metrics = metrics.copy() if metrics else {}
        if _key_values:
            metrics.update(_key_values)

        with self.Prefix(metrics=_prefix):
            if self.metrics_prefix:
                metrics = {self.metrics_prefix + k: v for k, v in metrics.items()}

        metrics.update({"__timestamp": timestamp})
        cache.update(metrics)
        if silent:
            # fixme: need to remove this causes subtle unexpected behaviors
            self.do_not_print.update(metrics.keys())

        if flush:
            self.flush_metrics(cache=cache_key, file=file)

    def log_key_value(self, key: str, value: Any, silent=False, cache=None) -> None:
        cache = self.key_value_caches[cache]
        timestamp = np.datetime64(self.now())
        if silent:
            # note: this causes subtle unexpected behaviors
            self.do_not_print.add(key)
        cache.update({key: value, "__timestamp": timestamp})

    @property  # get default cache
    def summary_cache(self):
        return self.summary_caches[None]

    def store_key_value(self, key: str, value: Any, silent=None, cache: Union[str, None] = None) -> None:
        """
        store the key: value awaiting future summary.

        :param key: str, can be `/` separated.
        :param value: numerical value
        :param silent:
        :param cache: 
        :return: 
        """
        self.store_metrics({key: value}, silent=silent, cache=cache)

    def store_metrics(self, metrics=None, silent=None, cache: Union[str, None] = None,
                      _prefix=None, **key_values):
        """
        Store the metric data (with the default summary cache) for making the summary later.
        This allows the logging/saving of training metrics asynchronously from the logging.

        :param * metrics: a mapping of metrics. Will be destructured and appended
                               to the data store one key/value at a time,
        :param silent: bool flag for silencing the keys stored in this call.
        :param cache:
        :param ** key_values: key/value arguments, each being a metric key / metric value pair.
        :return: None
        """
        cache = self.summary_caches[cache]
        if metrics:
            key_values.update(metrics)
        if silent:  # todo: deprecate this
            self.do_not_print.update(key_values.keys())

        with self.Prefix(metrics=_prefix):
            if self.metrics_prefix:
                key_values = {self.metrics_prefix + k: v for k, v in key_values.items()}
        cache.store(metrics, **key_values)

    store = store_metrics

    def peek_stored_metrics(self, *keys, len=5, print_only=True, cache=None):
        _ = self.summary_caches[cache].peek(*keys, len=len)
        output = self.print_helper.format_row_table(_, max_rows=len, do_not_print_list=self.do_not_print)
        (print if print_only else self.log_line)(output)

    def log_metrics_summary(self, key_values: dict = None,
                            cache: str = None, key_stats: dict = None,
                            default_stats=None, silent=False, flush: bool = True,
                            _prefix=None, **_key_modes) -> None:
        """
        logs the statistical properties of the stored metrics, and clears the
        `summary_cache` if under `tiled` mode, and keeps the data otherwise
        (under `rolling` mode).

        To enable explicit mode without specifying *only_keys, set
        `get_only` to True

        Modes for the Statistics:

        key_mode would be one of:
          - mean:
          - min_max:
          - std_dev:
          - quantile:
          - histogram(bins=10):


        :param key_values: extra key (and values) to log together with summary such as `timestep`, `epoch`, etc.
        :param cache: (dict) An optional cache object from which the summary is made.
        :param key_stats: (dict) a dictionary for the key and the statistic modes to be returned.
        :param default_stats: (one of ['mean', 'min_max', 'std_dev', 'quantile', 'histogram'])
        :param silent: (bool) a flag to turn the printing On/Off
        :param flush: (bool) flush the key_value cache if trueful.
        :param _key_modes: (**) key value pairs, as a short hand for the key_modes dictionary.
        :return: None
        """
        cache = self.summary_caches[cache]
        summary = cache.summarize(key_stats=key_stats, default_stats=default_stats, **_key_modes)
        if key_values:
            with self.Prefix(metrics=_prefix):
                if self.metrics_prefix:
                    key_values = {self.metrics_prefix + k: v for k, v in key_values}
            summary.update(key_values)

        with self.Prefix(metrics=False):
            # todo: use `summary` key to avoid interference with keyvalue metrics.
            #  self.log_metrics(metrics=summary, silent=silent, flush=flush, cache="summary")
            self.log_metrics(metrics=summary, silent=silent, flush=flush)

    def log(self, *args, metrics=None, silent=False, sep=" ", end="\n", flush=None,
            cache=None, file=None, _prefix=None, **_key_values) -> None:
        """
        log dictionaries of data, key=value pairs at step == step.

        logs *argss as line and kwargs as key / value pairs

        :param args: (str) strings or objects to be printed.
        :param metrics: (dict) a dictionary of key/value pairs to be saved in the key_value_cache
        :param sep: (str) separator between the strings in *args
        :param end: (str) string to use for the end of line. Default to "\n"
        :param silent: (boolean) whether to also print to stdout or just log to file
        :param flush: (boolean) whether to flush the text logs
        :param cache: optional (str) a specific cache key, useful for scoped reporting
        :param kwargs: key/value arguments
        :return:
        """
        if args:  # do NOT print the '\n' if args is empty in call. Different from the signature of the print function.
            self.log_line(*args, sep=sep, end=end, flush=False)
        if metrics:
            _key_values.update(metrics)
        self.log_metrics(metrics=_key_values, silent=silent, _prefix=_prefix, cache=cache, file=file, flush=flush)

    metric_filename = "metrics.pkl"
    log_filename = "outputs.log"

    def flush_metrics(self, cache=Union[None, str], file=Union[str, None]):
        cache = self.key_value_caches[cache]
        key_values = cache.pop_all()
        file = file or self.metric_filename
        output = self.print_helper.format_tabular(key_values, self.do_not_print)
        if output is not None:
            self.print(output, flush=True)  # not buffered
        self.client.log(key=pJoin(self.prefix, file), data=key_values)
        # fixme: this has caused trouble before.
        self.do_not_print.reset()

    def flush(self, cache=None, file=None):
        """Flushes the key_value cache and the print buffer"""
        # self.log_metrics_summary(flush=False)
        self.flush_metrics(cache, file)
        self.flush_print_buffer()

    uploaded_files = {}

    def upload_file(self, file_path: str = None, target_path: str = "files/", once=True) -> None:
        """
        uploads a file (through a binary byte string) to a target_folder. Default
        target is "files"

        :param file_path: the path to the file to be uploaded
        :param target_path: the target folder for the file, preserving the filename of the file.
            if end of `/`, uses the original file name.
        :return: None
        """
        if file_path in self.uploaded_files and once:
            return
        self.uploaded_files[file_path] = target_path

        from pathlib import Path
        bytes = Path(file_path).read_bytes()
        basename = [os.path.basename(file_path)] if target_path.endswith('/') else []
        self.client.log_buffer(key=pJoin(self.prefix, target_path, *basename), buf=bytes, overwrite=True)

    def upload_dir(self, dir_path, target_folder='', excludes=tuple(), gzip=True, unzip=False):
        """log a directory, or upload an entire directory."""
        raise NotImplementedError

    def save_images(self, stack, key, n_rows=None, n_cols=None, cmap=None, normalize=None, background=1):
        """Log images as a composite of a grid. Images input as a 4-D stack.

        :param stack: Size(n, w, h, c)
        :param key: the filename for the composite image.
        :param n_rows: number of rows
        :param n_cols: number of columns
        :param cmap: OneOf([str, matplotlib.cm.ColorMap])
        :param normalize: defaul None. OneOf[None, 'individual', 'row', 'column', 'grid']. Only 'grid' and
                          'individual' are implemented.
        :return: None
        """
        stack = stack if hasattr(stack, 'dtype') else np.stack(stack)

        n_cols = n_cols or len(stack)
        n_rows = n_rows or ceil(len(stack) / n_cols)

        if np.issubdtype(stack.dtype, np.uint8):
            pass
        elif len(stack.shape) == 3:
            from matplotlib import cm
            map_fn = cm.get_cmap(cmap or 'Greys')
            # todo: this needs to happen for each individual imagedata
            if normalize is None:
                pass
            elif normalize == 'individual':
                r = np.nanmax(stack, axis=(1, 2)) - np.nanmin(stack, axis=(1, 2))
                stack = (stack - np.nanmin(stack, axis=(1, 2))[:, None, None]) / \
                        np.select([r != 0], [r], 1)[:, None, None]
            elif normalize == 'grid':
                stack = (stack - np.nanmin(stack)) / (np.nanmax(stack) - np.nanmin(stack) or 1)
            elif isinstance(normalize, Sequence):
                low, high = normalize
                low = np.nanmin(stack) if low is None else low
                high = np.nanmax(stack) if high is None else high
                stack = (stack - low) / (high - low or 1)
            else:
                raise NotImplementedError(f'for normalize = {normalize}')
            stack = (map_fn(stack) * 255).astype(np.uint8)
        elif len(stack.shape) == 4:
            assert cmap is None, "color map is not used for rgb(a) images."
            stack = (stack * 255).astype(np.uint8)
        else:
            raise RuntimeError(f"{stack.shape} is not supported. `len(shape)` should be 3 "
                               f"for gray scale  and 4 for RGB(A).")

        assert np.issubdtype(stack.dtype, np.uint8), "the image type need to be unsigned 8-bit."
        n, h, w, *c = stack.shape
        # todo: add color background -- need to decide on which library to use.
        composite = np.full([h * n_rows, w * n_cols, *c], background, dtype='uint8')
        for i in range(n_rows):
            for j in range(n_cols):
                k = i * n_cols + j
                if k >= n:
                    break
                # todo: remove last index
                composite[i * h: i * h + h, j * w: j * w + w] = stack[k]

        self.client.send_image(key=pJoin(self.prefix, key), data=composite)

    def save_image(self, image, key: str, cmap=None, normalize=None):
        """Log a single image.

        :param image: numpy object Size(w, h, 3)
        :param key: example: "figures/some_fig_name.png", the file key to which the
            image is saved.
        """
        self.save_images([image], key, n_rows=1, n_cols=1, cmap=cmap, normalize=normalize)

    def save_video(self, frame_stack, key, format=None, fps=20, **imageio_kwargs):
        """
        Let's do the compression here. Video frames are first written to a temporary file
        and the file containing the compressed data is sent over as a file buffer.

        Save a stack of images to

        :param frame_stack: the stack of video frames
        :param key: the file key to which the video is logged.
        :param format: Supports 'mp4', 'gif', 'apng' etc.
        :param imageio_kwargs: (map) optional keyword arguments for `imageio.mimsave`.
        :return:
        """
        if format:
            key += "." + format
        else:
            # noinspection PyShadowingBuiltins
            _, format = os.path.splitext(key)
            if format:
                # noinspection PyShadowingBuiltins
                format = format[1:]  # to remove the dot
            else:
                # noinspection PyShadowingBuiltins
                format = "mp4"
                key += "." + format

        filename = pJoin(self.prefix, key)
        import tempfile, imageio  # , logging as py_logging
        # py_logging.getLogger("imageio").setLevel(py_logging.WARNING)
        with tempfile.NamedTemporaryFile(suffix=f'.{format}') as ntp:
            from skimage import img_as_ubyte
            try:
                imageio.mimsave(ntp.name, img_as_ubyte(frame_stack), format=format, fps=fps, **imageio_kwargs)
            except imageio.core.NeedDownloadError:
                imageio.plugins.ffmpeg.download()
                imageio.mimsave(ntp.name, img_as_ubyte(frame_stack), format=format, fps=fps, **imageio_kwargs)
            ntp.seek(0)
            self.client.log_buffer(key=filename, buf=ntp.read(), overwrite=True)

    # todo: incremental save pyplot to video.
    # def VideoContext(self, fig = None)
    #     yield blah

    def save_pyplot(self, path="plot.png", fig=None, format=None, **kwargs):
        """
        Saves matplotlib figure. The interface of this method emulates `matplotlib.pyplot.savefig`
            method.

        :param key: (str) file name to which the plot is saved.
        :param fig: optioanl matplotlib figure object. When omitted just saves the current figure.
        :param format: One of the output formats ['pdf', 'png', 'svg' etc]. Default to the extension
            given by the ``key`` argument in :func:`savefig`.
        :param `**kwargs`: other optional arguments that are passed into
            _matplotlib.pyplot.savefig: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.savefig.html
        :return: (str) path to which the figure is saved to.
        """
        # can not simplify the logic, because we can't pass the filename to pyplot. A buffer is passed in instead.
        if format:  # so allow key with dots in it: metric_plot.text.plot + ".png". Because user intention is clear
            path += "." + format
        else:
            _, format = os.path.splitext(path)
            if format:
                format = format[1:]  # to get rid of the "." at the begining of '.svg'.
            else:
                format = "png"
                path += "." + format

        if fig is None:
            from matplotlib import pyplot as plt
            fig = plt.gcf()

        buf = BytesIO()
        fig.savefig(buf, format=format, **kwargs)
        buf.seek(0)

        path = pJoin(self.prefix, path)
        self.client.log_buffer(path, buf.read(), overwrite=True)
        return path

    def savefig(self, key, fig=None, format=None, **kwargs):
        """
        Saves matplotlib figure. The interface of this method emulates `matplotlib.pyplot.savefig`
            method.

        :param key: (str) file name to which the plot is saved.
        :param fig: optioanl matplotlib figure object. When omitted just saves the current figure.
        :param format: One of the output formats ['pdf', 'png', 'svg' etc]. Default to the extension
            given by the ``key`` argument in :func:`savefig`.
        :param `**kwargs`: other optional arguments that are passed into
            _matplotlib.pyplot.savefig: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.savefig.html
        :return: (str) path to which the figure is saved to.
        """
        return self.save_pyplot(path=key, fig=fig, format=format, **kwargs)

    def save_module(self, module, path="weights.pkl", tries=3, backup=3.0):
        """
        Save torch module. Overwrites existing file.

        Now Supports `nn.DataParallel` modules. First
        try to access the state dict, if not available
        try the module.module attribute.

        .. code:: python

            module = nn.DataParallel(lenet)
            logger.save_module(module, "checkpoint.pk")

        When the model is large, this function uploads the weight dictionary (state_dict) in
        chunks. You can specify the size for the chunks, measured in number of tensors.

        The conversion convention for the upload chunks is roughly 32bit, or 8 bytes for each
        `np.float32` entry. so the upload size for chunk = 100,000 is roughly

            100_000 * 8 * <base56 encoding ration> ~ 960k.

        :param module: the PyTorch module to be saved.
        :param path: filename to which we save the module.

        :return: None
        """
        # todo: add
        if hasattr(module, "state_dict"):
            state_dict = module.state_dict()
        elif hasattr(module, "module"):
            state_dict = module.module.state_dict()
        else:
            raise AttributeError('module does not have `.state_dict` attribute or a valid `.module`.')

        return self.save_torch(state_dict, path=path, tries=tries, backup=backup)

    def read_state_dict(self, path="weights.pkl", wd=None, stream=True, tries=5, matcher=None, map_location=None):
        if "*" in path:
            all_paths = self.glob(path, wd=wd)
            if len(all_paths) == 0:
                raise FileNotFoundError(f"Path matching {path} is not found")
            path = pJoin(wd or "", sorted(all_paths)[-1])

        return self.load_torch(path, map_location=map_location)

    def load_module(self, module, path="weights.pkl", wd=None, stream=True, tries=5, matcher=None,
                    map_location=None):
        """
        Load torch module from file.

        Now supports:

        - streaming mode: where multiple segments of the same model is
            saved as chunks in a pickle file.
        - partial, or prefixed load with :code:`matcher`.
        - multiple tires: on unreliable networks (coffee shop!)

        To manipulate the prefix of a checkpoint file you can do

        Using Matcher for Partial or Prefixed load

        Imaging you are trying to load weights from a different module
        that is missing a prefix for their keys. (For example you
        have a L2 metric function, and is trying to load from a VAE
        embedding function baseline (only half of the netowrk)).

        .. code:: python

            from ml_logger import logger

            net = models.ResNet()
            logger.load_module(
                   net,
                   path="/checkpoint/geyang/resnet.pkl",
                   matcher=lambda d, k, p: d[k.replace('embed.')])

        To fill-in if there are missing keys:

        .. code:: python

            from ml_logger import logger

            net = models.ResNet()
            logger.load_module(
                   net,
                   path="/checkpoint/geyang/resnet.pkl",
                   matcher=lambda d, k, p: d[k] if k in d else p[k])

        :param module: target torch module you want to load
        :param path: the weight file containing the weights
        :param stream:
        :param tries:
        :param matcher: function to remove prefix, repeat keys, partial load (by).
                    Should take in 2 or three arguments:

                    .. code:: python

                        def matcher(checkpoint_dict, key, current_dict):
        :return: None
        """
        state_dict = self.read_state_dict(path=path, wd=wd, stream=stream, tries=tries, matcher=matcher,
                                          map_location=map_location)
        assert state_dict, f"the datafile can not be empty: [state_dict == {{{state_dict.keys()}...}}]"

        module.load_state_dict(state_dict)

    def save_variables(self, variables, path="variables.pkl", keys=None):
        """
        save tensorflow variables in a dictionary

        :param variables: A Tuple (Array) of TensorFlow Variables.
        :param path: default: 'variables.pkl', filepath to the pkl file, with which we save the variable values.
        :param namespace: A folder name for the saved variable. Default to `./checkpoints` to keep things organized.
        :param keys: None or Array(size=len(variables)). When is an array the length has to be the same as that of
        the list of variables. This parameter allows you to overwrite the key we use to save the variables.

        By default, we generate the keys from the variable name, without the `:[0-9]` at the end that points to the
        tensor (from the variable itself).
        :return: None
        """
        # todo: need to upgrade to the multi-part upload scheme
        if keys is None:
            keys = [v.name for v in variables]
        assert len(keys) == len(variables), 'the keys and the variables have to be the same length.'
        import tensorflow.compat.v1 as tf
        sess = tf.get_default_session()
        vals = sess.run(variables)
        weight_dict = {k.split(":")[0]: v for k, v in zip(keys, vals)}
        logger.save_pkl(weight_dict, path)

    def load_variables(self, path, variables=None):
        """
        load the saved value from a pickle file into tensorflow variables.

        The variables that are loaded is the intersection between the tf.global_variables() list and the
        variables saved in the weight_dict. When a variable in the weight_dict is not present in the
        current session's computation graph, no error is reported. When a variable present in the global
        variables list is not present in the weight_dict, no exception is raised.

        The variables argument overrides the global variable list. When a variable present in this list doesn't
        exist in the weight list, an exception should be raised.

        :param path: path to the saved checkpoint pickle file.
        :param variables: None or a list of tensorflow variables. When this list is supplied,
            every variable's truncated name has to exist inside the loaded weight_dict.
        :return:
        """
        import tensorflow.compat.v1 as tf
        weight_dict, = logger.load_pkl(path)
        sess = tf.get_default_session()
        if variables:
            for v in variables:
                key, *_ = v.name.split(':')
                val = weight_dict[key]
                v.load(val, sess)
        else:
            # for k, v in weight_dict.items():
            for v in tf.global_variables():
                key, *_ = v.name.split(':')
                val = weight_dict.get(key, None)
                if val is None:
                    continue
                v.load(val, sess)

    def load_text(self, *keys):
        """ return the text content of the file (in a single chunk)

        todo: check handling of line-separated files

        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        :param *keys: path string fragments
        :return: a tuple of each one of the data chunck logged into the file.
        """
        return self.client.read_text(pJoin(self.prefix, *keys))

    def load_jsonl(self, *keys, start=None, stop=None, tries=1, delay=1):
        path = pJoin(self.prefix, *keys)
        while tries > 1:
            try:
                with BytesIO() as buf:
                    blobs = self.client.read(path, start, stop)
                    for blob in blobs:
                        buf.write(blob)
                    buf.seek(0)
                    return list(load_from_jsonl_file(buf))
            except Exception as e:
                # todo: use separate random generator to avoid mutating global random generator.
                sleep((1 + random() * 0.5) * delay)
                tries -= 1
        # last one does not catch.
        with BytesIO() as buf:
            chunks = self.client.read(path, start, stop)
            for chunk in chunks:
                buf.write(chunk)
            buf.seek(0)
            return list(load_from_jsonl_file(buf))

    def save_torch(self, obj, *keys, path=None, tries=3, backup=3.0):
        path = pJoin(self.prefix, *keys, path)
        import torch
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(delete=True) as tfile:
            torch.save(obj, tfile)

            while tries > 0:
                tries -= 1
                tfile.seek(0)
                try:
                    self.client.save_file(source_path=tfile.name, key=path)
                except Exception as e:
                    if tries == 0:
                        raise e
                    dt = random() * backup
                    self.print(f"{tries} left, saving to {path} again. Backup for {dt:0.3f} sec...")
                    sleep(dt)

    torch_save = save_torch

    def load_file(self, *keys, path=None):
        """ return the binary stream, most versatile.

        todo: check handling of line-separated files

        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        :param *keys: path string fragments that are joined together
        :return: a tuple of each one of the data chunck logged into the file.
        """
        path = pJoin(self.prefix, *keys, path)
        return self.client.stream_download(path)

    def download_file(self, *keys, path=None, to, relative=False):
        buf = self.load_file(*keys)
        path = pJoin(*keys, path)
        if relative:
            to = pJoin(to, path)
        elif to.endswith('/'):
            to += os.path.basename(path)
        os.makedirs(os.path.dirname(to), exist_ok=True)
        with open(to, "wb") as f:
            f.write(buf.getbuffer())

    def load_torch(self, *keys, map_location=None, **kwargs):
        import torch
        buf = self.load_file(*keys)
        return torch.load(buf, map_location=map_location, **kwargs)

    torch_load = load_torch

    def load_pkl(self, *keys, start=None, stop=None, tries=1, delay=1):
        """
        load a pkl file *as a tuple*. By default, each file would contain 1 data item.

        .. code:: python

            data, = logger.load_pkl("episodeyang/weights.pkl")

        You could also load a particular data chunk by index:

        .. code:: python

            data_chunks = logger.load_pkl("episodeyang/weights.pkl", start=10)


        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        Because loading is usually synchronous, we can encounter connection errors. We don't want
        to halt our training session b/c of these errors without retrying a few times.

        For this reason, `logger.load_pkl` (and `iload_pkl` to equal measure) both takes a `tries`
        argument and a `delay` argument. The delay argument is multipled by a random number,
        to avoid synchronized DDoS attach on your instrumentation server.


        tries

        :param *keys: path string fragments
        :param start: Starting index for the chunks None means from the beginning.
        :param stop: Stop index for the chunks. None means to the end of the file.
        :param tries: (int) The number of ties for the request. The last one does not catch error.
        :param delay: (float) the delay multiplier between the retries. Multiplied (in seconds) with
            a random float in [1, 1.5).
        :return: a tuple of each one of the data chunck logged into the file.
        """
        path = pJoin(self.prefix, *keys)
        while tries > 1:
            try:
                with BytesIO() as buf:
                    blobs = self.client.read(path, start, stop)
                    for blob in blobs:
                        buf.write(blob)
                    buf.seek(0)
                    return list(load_from_pickle_file(buf))
            except Exception as e:
                import random
                # todo: use separate random generator to avoid mutating global random generator.
                sleep((1 + random.random() * 0.5) * delay)
                tries -= 1
        # last one does not catch.
        with BytesIO() as buf:
            chunks = self.client.read(path, start, stop)
            for chunk in chunks:
                buf.write(chunk)
            buf.seek(0)
            return list(load_from_pickle_file(buf))

    def iload_pkl(self, key, **kwargs):
        """
        load a pkl file as *an iterator*.

        .. code:: python

            for chunk in logger.iload_pkl("episodeyang/weights.pkl")
                print(chunk)

         or alternatively just read a single data file:

        .. code:: python

            data, = logger.iload_pkl("episodeyang/weights.pkl")

        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        :param key: path string.
        :param start: Starting index for the chunks None means from the beginning.
        :param stop: Stop index for the chunks. None means to the end of the file.
        :param tries: (int) The number of ties for the request. The last one does not catch error.
        :param delay: (float) the delay multiplier between the retries. Multiplied (in seconds) with
            a random float in [0, 1).
        :return: a iterator.
        """
        i = 0
        while True:
            chunks = self.load_pkl(key, start=i, stop=i + 1, **kwargs)
            i += 1
            if not chunks:
                break
            yield from chunks

    def load_np(self, *keys):
        """ load a np file

        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        :param keys: path strings
        :return: a tuple of each one of the data chunck logged into the file.
        """
        return self.client.read_np(pJoin(self.prefix, *keys))

    def load_json(self, *keys):
        return self.client.read_json(pJoin(self.prefix, *keys))

    def load_yaml(self, *keys):
        import yaml
        text = self.client.read_text(pJoin(self.prefix, *keys))
        return yaml.load(text)

    def load_h5(self, *keys):
        return self.client.read_h5(pJoin(self.prefix, *keys))

    @staticmethod
    def plt2data(fig):
        """

        @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
        @param fig a matplotlib figure
        @return a numpy 3D array of RGBA values
        """
        # draw the renderer
        fig.canvas.draw_idle()  # need this if 'transparent=True' to reset colors
        fig.canvas.draw()
        # Get the RGBA buffer from the figure
        w, h = fig.canvas.get_width_height()
        buf = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf.shape = (h, w, 3)
        # todo: use alpha RGB instead
        # buf.shape = (h, w, 4)
        # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
        # buf = np.roll(buf, 4, axis=2)
        return buf

    def save_json(self, data, file):
        import json
        self.log_text(json.dumps(data), file, overwrite=True)

    def save_yaml(self, data, file):
        import yaml
        self.log_text(yaml.dump(data), file, overwrite=True)

    def save_h5(self, data, key):
        raise NotImplementedError

    # todo: make buffer is keyed by file name
    # todo: add option to save non-colored logs.
    def log_line(self, *args, sep=' ', end='\n', flush=True, file=None, **kwargs):
        """
        this is similar to the print function. It logs *args with a default EOL postfix in the end.

        .. code:: python

            n = 10
            logger.log_line("Mary", "has", n, "sheep.", color="green")

        This outputs:

        ::

            >>> "Mary has 10 sheep" (colored green)

        :param *args: List of object to be converted to string and printed out.
        :param sep: Same as the `sep` kwarg in regular print statements
        :param end: Same as the `end` kwarg in regular print statements
        :param flush: bool, whether the output is flushed. Default to True
        :param file: file object to which the line is written
        :param color: str, color of the line. We use `termcolor.colored` as our color library. See list of
            colors here: _`termcolor`: https://pypi.org/project/termcolor/
        :return: None
        """
        text = sep.join([str(a) for a in args]) + end
        self.print_buffer += text
        # todo: print_buffer is not keyed by file. This is a bug.
        if flush or file or len(self.print_buffer) > self.print_buffer_size:
            self.flush_print_buffer(file=file, **kwargs)

    def print(self, *args, sep=' ', end='\n', flush=True, file=None, color=None, dedent=False, **kwargs):
        text = sep.join([str(a) for a in args])
        if dedent:
            import textwrap
            text = textwrap.dedent(text).lstrip()

        if color:
            from termcolor import colored
            text = colored(text, color)
        print(text, end=end)
        self.log_line(*args, sep=sep, end=end, flush=flush, file=file, **kwargs)

    def pprint(self, object=None, indent=None, width=None, depth=None, **kwargs):
        from pprint import pformat
        return self.print(pformat(object, indent, width, depth), **kwargs)

    def flush_print_buffer(self, file=None, **kwargs):
        if self.print_buffer:
            self.log_text(self.print_buffer, filename=file, **kwargs)
        self.print_buffer = ""

    def log_text(self, text: str = None, filename=None, dedent=False, overwrite=False):
        """
        logging and printing a string object.

        This does not log to the buffer. It calls the low-level log_text method right away
        without buffering.

        .. code:: python

            logger.log_text('''
                some text
                with indent''', dedent=True)

        This logs with out the indentation at the begining of the text.

        :param text:
        :param filename: file name to which the string is logged.
        :param dedent: boolean flag for dedenting the multi-line string
        :return:
        """
        filename = filename or self.log_filename
        if text is None:
            return

        text = str(text)
        if dedent:
            import textwrap
            text = textwrap.dedent(text).lstrip()

        self.client.log_text(key=pJoin(self.prefix, filename), text=text, overwrite=overwrite)

    def glob(self, query, wd=None, recursive=True, start=None, stop=None):
        """
        Globs files under the work directory (`wd`). Note that `wd` affects the file paths
        being returned. The default is the current logging prefix. Use absolute path (with
        a leanding slash (`/`) to escape the logging prefix. Use two leanding slashes for
        the absolute path in the host for the logging server.

        .. code:: python

            with logger.PrefixContext("<your-run-prefix>"):
                runs = logger.glob('**/metrics.pkl')
                for _ in runs:
                    exp_log = logger.load_pkl(_)

        :param query:
        :param wd: defaults to the current prefix. When trueful values are given, uses:
            > wd = pJoin(self.prefix, wd)

            if you want root of the logging server instance, use abs path headed by `/`.
            If you want root of the server file system, double slash: `//home/directory-name-blah`.

        :param recursive:
        :param start:
        :param stop:
        :return: None if the director does not exist (internal FileNotFoundError)
        """
        if not wd and query.startswith('/'):
            return ['/' + p for p in
                    self.client.glob(query, wd="/", recursive=recursive, start=start, stop=stop)]

        wd = pJoin(self.prefix, wd or "")
        return self.client.glob(query, wd=wd, recursive=recursive, start=start, stop=stop)

    def get_parameters(self, *keys, path="parameters.pkl", silent=False, **kwargs):
        """
        utility to obtain the hyperparameters as a flattened dictionary.

        1. returns a dot-flattened dictionary if no keys are passed.
        2. returns a single value if only one key is passed.
        3. returns a list of values if multiple keys are passed.

        If keys are passed, returns an array with each item corresponding to those keys

        .. code:: python

            lr, global_metric = logger.get_parameters('Args.lr', 'Args.global_metric')
            print(lr, global_metric)

        this returns:

        .. code:: bash

            0.03 'ResNet18L2'

        Raises `FileNotFound` error if the parameter file pointed by the path is empty. To
        avoid this, add a `default` keyword value to the call:

        .. code:: python

            param = logger.get_parameter('does_not_exist', default=None)
            assert param is None, "should be the default value: None"


        :param *keys: A list of strings to specify the parameter keys
        :param silent: bool, prevents raising an exception.
        :param path: Path to the parameters.pkl file. Keyword argument, default to `parameters.pkl`.
        :param default: Undefined. If the default key is present, return default when param is missing.
        :return:
        """
        _ = self.load_pkl(path)
        if _ is None:
            if keys and keys[-1] and "parameters.pkl" in keys[-1]:
                self.print('Your last key looks like a `parameters.pkl` path. Make '
                           'sure you use a keyword argument to specify the path!', color="yellow")
            if silent:
                return
            raise FileNotFoundError(f'the parameter file is not found at {path}')

        from functools import reduce
        from ml_logger.helpers.func_helpers import assign, dot_flatten
        parameters = dot_flatten(reduce(assign, _))
        if len(keys) > 1:
            # info: cast to tuple, so that we can use this as a key in dict directly.
            return tuple(parameters.get(k, kwargs['default']) if 'default' in kwargs else parameters[k] for k in keys)
        elif len(keys) == 1:
            return parameters.get(keys[0], kwargs['default']) if 'default' in kwargs else parameters[keys[0]]
        else:
            return parameters

    read_params = get_parameters

    def read_metrics(self, *keys, bin: BinOptions = None, path="metrics.pkl", wd=None, silent=False, default=None,
                     collect="std", verbose=False):
        """
        Returns a Pandas.DataFrame object that contains metrics from all files.

        :param keys: if non passed, returns the entire dataframe. If 1 key is passed,
                     return that column. If multiple keys are passed, return  individual columns.

                     If you want to get the joined table for multiple keys, directly filter after
                     this call.

        :param bin: binOption(xKey, n, steps)
        :param path: can contain glob patterns, will return concatenated dataframe from
                     all paths found with the pattern.
        :param silent:
        :param default: Default value for columns. Not widely used.
        :param collect: One of [ "std", True, False ]
        :param kwargs: Not used besides the default argument.
        :return: pandas.DataFrame or None when no metric file is found.
        """
        import pandas as pd
        from contextlib import ExitStack

        if bin is not None:
            assert not keys or bin.key in keys, f"bin.key need to be in keys {keys}"
            if bin.n:
                assert bin.size is None, f"n and size are exclusive {bin}"

        if keys:
            meta_keys = defaultdict(list)
            for k in keys:
                k, *aggs = k.split("@")
                meta_keys[k].extend(aggs)

            keys, query_keys = [*meta_keys.keys()], keys

        # todo: remove default from this.
        paths = self.glob(path, wd=wd) if "*" in path else [path]
        if verbose:
            print(*paths, sep="\n")

        if not paths:
            return None

        all_metrics = {}
        for path in paths:
            with self.PrefixContext(wd) if wd else ExitStack():
                if path.endswith(".jsonl"):
                    metrics = self.load_jsonl(path)
                elif path.endswith(".pkl"):
                    metrics = self.load_pkl(path)
                elif path.endswith(".csv"):
                    metrics = self.load_csv(path)
            if metrics is None:
                if keys and keys[-1] and (
                        ".pkl" in keys[-1] or
                        ".jsonl" in keys[-1] or
                        ".csv" in keys[-1]
                ):
                    self.log_line('Your last key looks like a `metrics.pkl` path. Make '
                                  'sure you use a keyword argument to specify the path!',
                                  color="yellow")
                if silent:
                    return
                raise FileNotFoundError(f'fails to load metric file at {path}')

            if verbose:
                from IPython.core.display import display, HTML
                url = os.path.normpath(pJoin(wd or self.prefix, path, "../.."))
                display(HTML(f"""<a href="http://localhost:3001{url}">{path}</a>"""))
                # self.print(f"loaded:", path, flush=True)

            df = pd.DataFrame(metrics)
            if keys:
                try:
                    df = df[keys].dropna()
                except KeyError:
                    continue

            if bin is not None:
                if bin.n:
                    bins = pd.qcut(df[bin.key], bin.n, duplicates="drop")
                elif bin.size:
                    bins = pd.cut(df[bin.key], bin.size)

                new_df = {}
                grouped = df.groupby(bins)
                for k in keys or df.keys():
                    if k == bin.key:
                        new_df[bin.key] = grouped[bin.key].agg('min')
                    else:
                        try:
                            new_df[k] = grouped[k].agg("mean")
                        except Exception:
                            new_df[k] = float('nan')
                df = pd.DataFrame(new_df).reset_index(drop=True)

            all_metrics[path] = pd.DataFrame(df)

        if not keys:
            return all_metrics

        df = pd.concat(all_metrics.values())

        if bin is not None:
            df = df.set_index(bin.key).sort_values(by=bin.key).reset_index()
            if bin.n:
                bins = pd.qcut(df[bin.key], bin.n, duplicates="drop")
            elif bin.size:
                bins = pd.cut(df[bin.key], bin.size)
        else:
            bins = df.index

        grouped = df.groupby(bins)
        new_df = {}
        for k, aggs in meta_keys.items():
            if k == (bin.key if bin else keys[0]):
                new_df[k] = grouped[k].agg("min")
            else:
                new_df[k] = grouped[k].mean()
                new_df[k + "@mean"] = grouped[k].mean()
                for reduce in aggs:
                    if reduce.endswith("%"):
                        pc = float(reduce[:-1])
                        new_df[k + "@" + reduce] = grouped[k].quantile(0.01 * pc)
                    else:
                        new_df[k + "@" + reduce] = grouped[k].agg(reduce)

        df = pd.DataFrame(new_df)

        # apply bin, min@x, mean@y, etc.
        if len(keys) > 1:
            return [df.get(k, default or None) for k in query_keys]
        elif len(keys) == 1:
            return df.get(query_keys[0], default or None)
        return metrics

    get_dataframe = read_metrics

    def abspath(self, *paths):
        """
        returns the absolute path w.r.t the logging directory.

        .. code:: python

            print(logger.abspath("some", "path"))

            # /home/ge/some/path


        :param *paths: position arguments for each segment of the path.
        :return: absolute path w.r.t. the logging directory (excluding the prefix)
        """
        if self.prefix.startswith("/"):
            return pJoin(self.prefix, *paths)
        return "/" + pJoin(self.prefix, *paths)

    @contextmanager
    def capture_error(self, file="error.log", reraise=False):
        try:
            yield
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with logger.SyncContext():  # Make sure uploaded finished before termination.
                logger.print("Exception occurred", e, tb, file=file, flush=True)
            if reraise:
                raise e


logger = ML_Logger()
