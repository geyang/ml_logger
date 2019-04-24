import os
from contextlib import contextmanager

import numpy as np
from collections.abc import Sequence
from io import BytesIO
from numbers import Number
from typing import Any

from termcolor import cprint

from .helpers.default_set import DefaultSet
from .full_duplex import Duplex
from .log_client import LogClient
from .helpers.print_utils import PrintHelper
from .caches.key_value_cache import KeyValueCache
from .caches.summary_cache import SummaryCache
from .helpers.color_helpers import Color


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
def _PrefixContext(logger, new_prefix):
    old_prefix = logger.prefix
    logger.prefix = new_prefix
    try:
        yield
    finally:
        logger.prefix = old_prefix


# @contextmanager
# def _LocalContext(logger, new_prefix=None):
#     old_client = logger.client
#     logger.prefix = new_prefix
#     try:
#         yield
#     finally:
#         logger.prefix = old_prefix


# noinspection PyPep8Naming
class ML_Logger:
    """
    ML_Logger, a logging utility for ML training.
    ---



    """
    client = None
    log_directory = None

    prefix = ""  # is okay b/c strings are immutable in python
    print_buffer = None  # move initialization to init.
    print_buffer_size = 2048

    summary_cache: SummaryCache

    ### Context Helpers
    def PrefixContext(self, *praefixa):
        """
        Returns a context in which the prefix of the logger is set to `prefix`
        :param praefixa: the new prefix
        :return: context object
        """
        return _PrefixContext(self, os.path.join(*praefixa))

    def SyncContext(self, clean=False, **kwargs):
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

    def AsyncContext(self, clean=False, **kwargs):
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

    # noinspection PyInitNewSignature
    def __init__(self, log_directory: str = None, prefix=None, buffer_size=2048, max_workers=None,
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

        :param log_directory: the server host and port number
        :param prefix: the prefix path
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

        # initialize caches
        self.key_value_cache = KeyValueCache()
        self.summary_cache = SummaryCache(**(summary_cache_opts or {}))

        # todo: add https support
        self.log_directory = log_directory or os.getcwd()
        if prefix is not None:
            assert not os.path.isabs(prefix), "prefix can not start with `/` because it is relative to `log_directory`."
            self.prefix = prefix

        # logger client contains thread pools, should not be re-created lightly.
        self.client = LogClient(url=self.log_directory, asynchronous=asynchronous, max_workers=max_workers)

    def configure(self,
                  log_directory: str = None,
                  prefix=None,
                  asynchronous=None,
                  max_workers=None,
                  buffer_size=None,
                  summary_cache_opts: dict = None,
                  register_experiment=True
                  ):
        """
        Configure an existing logger with updated configurations.

        # LogClient Behavior

        The logger.client would be re-constructed if

            - log_directory is changed
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

        todo: I'm considering also clearing this buffer also when summary-cache is
          updated.
              The use-case of changing print_buffer_size is pretty small. Should probaly
          just deprecate this.

        # Registering New Experiment

        This is a convinient default for new users. It prints out a dashboard link to
        the dashboard url.

        todo: the table at the moment seems a bit verbose. I'm considering making this
          just a single line print.

        :param log_directory:
        :param prefix:
        :param buffer_size:
        :param summary_cache_opts:
        :param asynchronous:
        :param max_workers:
        :param register_experiment:
        :return:
        """

        # path logic
        log_directory = log_directory or os.getcwd()
        if prefix is not None:
            assert not os.path.isabs(prefix), "prefix can not start with `/` because it is relative to `log_directory`."
            self.prefix = prefix

        if buffer_size is not None:
            self.print_buffer_size = buffer_size
            self.print_buffer = ""

        if summary_cache_opts is not None:
            self.key_value_cache.clear()
            self.summary_cache = SummaryCache(**(summary_cache_opts or {}))

        if asynchronous is not None or max_workers is not None or log_directory != self.log_directory:
            # note: logger.configure shouldn't be called too often, so it is okay to assume
            #   that we can discard the old logClient.
            #       To quickly switch back and forth between synchronous and asynchronous calls,
            #   use the `SyncContext` and `AsyncContext` instead.
            cprint('creating new logging client...', 'yellow', end=' ')
            self.log_directory = log_directory
            self.client.__init__(url=self.log_directory, asynchronous=asynchronous, max_workers=max_workers)
            cprint('✓ done', 'green')

        # now register the experiment
        if register_experiment:
            with logger.SyncContext(clean=True):  # single use SyncContext
                self.log_params(run=self.run_info())

    def run_info(self, **kwargs):
        if self.log_directory.startswith("http://"):
            host, port = self.log_directory[7:].split(":")
            run_info = dict(dashboard=ML_DASH.format(host=host, prefix=self.prefix))
        else:
            run_info = dict(log_directory=self.log_directory)
        run_info['createTime'] = self.now()
        run_info['prefix'] = self.prefix
        run_info.update(kwargs)
        return run_info

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
        from inspect import getmembers
        _ = dict(getmembers(fn))
        info = dict(name=_['__name__'], doc=_['__doc__'], module=_['__module__'], file=_['__globals__']['__file__'])
        return info

    def rev_info(self):
        return dict(hash=self.__head__, branch=self.__current_branch__)

    # timing functions
    def split(self):
        """
        returns a datetime object. You can get integer seconds and miliseconds (both int) from it.
        Note: This is Not idempotent, which is why it is not a property.

        :return: float (seconds/miliseconds)
        """
        new_tic = self.now()
        try:
            dt = new_tic - self._tic
            self._tic = new_tic
            return dt.total_seconds()
        except AttributeError:
            self._tic = new_tic
            return None

    def now(self, fmt=None):
        """
        This is not idempotent--each call returns a new value. So it has to be a method

        returns a datetime object if no format string is specified.
        Otherwise returns a formated string.

        Each call returns the current time.

        :param fmt: formating string, i.e. "%Y-%m-%d-%H-%M-%S-%f"
        :return: OneOf[datetime, string]
        """
        from datetime import datetime
        now = datetime.now()
        return now.strftime(fmt) if fmt else now

    def stem(self, path):
        """
        returns the stem of the filename in the path.

        :param path: "learning-to-learn/experiments/run.py"
        :return: "run"
        """
        return os.path.splitext(os.path.basename(path))[0]

    def diff(self, diff_directory=".", diff_filename="index.diff", silent=False):
        """
        example usage:
        --------------

        .. code:: python

            from ml_logger import logger

            logger.diff()  # => this writes a diff file to the root of your logging directory.

        :param diff_directory: The root directory to call `git diff`, default to current directory.
        :param diff_filename: The file key for saving the diff file.
        :return: None
        """
        import subprocess
        try:
            cmd = f'cd "{os.path.realpath(diff_directory)}" && git status -vv'
            if not silent: self.log_line(cmd)
            p = subprocess.check_output(cmd, shell=True)  # Save git diff to experiment directory
            patch = p.decode('utf-8').strip()
            self.log_text(patch, diff_filename, silent=silent)
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
        abs_path = os.path.join(self.prefix, path)
        self.client._delete(abs_path)

    def log_params(self, path="parameters.pkl", **kwargs):
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
            self.log_line(*table, sep="\n")
        self.log_data(path=path, data=_kwargs)

    def log_data(self, data, path=None, overwrite=False):
        """
        Append data to the file located at the path specified.

        :param data: python data object to be saved
        :param path: path for the object, relative to the root logging directory.
        :param overwrite: boolean flag to switch between 'appending' mode and 'overwrite' mode.
        :return: None
        """
        path = path or "data.pkl"
        abs_path = os.path.join(self.prefix, path)
        kwargs = {"key": abs_path, "data": data}
        if overwrite:
            kwargs['overwrite'] = overwrite
        self.client.log(**kwargs)

    def log_metrics(self, metrics=None, silent=None, cache: KeyValueCache = None, flush=None, **_key_values) -> None:
        """

        :param metrics: (mapping) key/values of metrics to be logged. Overwrites previous value if exist.
        :param silent: adds the keys being logged to the silent list, do not print out in table when flushing.
        :param cache: optional KeyValueCache object to be passed in
        :param flush:
        :param _key_values:
        :return:
        """
        cache = cache or self.key_value_cache
        timestamp = np.datetime64(self.now())
        metrics = metrics.copy() if metrics else {}
        if _key_values:
            metrics.update(_key_values)
        if silent:
            self.do_not_print.update(metrics.keys())
        metrics.update({"__timestamp": timestamp})
        cache.update(metrics)
        if flush:
            self.flush_metrics(cache=cache)

    def log_key_value(self, key: str, value: Any, silent=False, cache=None) -> None:
        cache = cache or self.key_value_cache
        timestamp = np.datetime64(self.now())
        if silent:
            self.do_not_print.add(key)
        cache.update({key: value, "__timestamp": timestamp})

    def store_metrics(self, metrics=None, silent=None, cache: SummaryCache = None, **key_values):
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
        cache = cache or self.summary_cache
        if metrics:
            key_values.update(metrics)
        if silent:
            self.do_not_print.update(key_values.keys())
        cache.store(metrics, **key_values)

    def peek_stored_metrics(self, *keys, len=5, print_only=True):
        _ = self.summary_cache.peek(*keys, len=len)
        output = self.print_helper.format_row_table(_, max_rows=len, do_not_print_list=self.do_not_print)
        (print if print_only else self.log_line)(output)

    def log_metrics_summary(self, key_values: dict = None, cache: SummaryCache = None, key_stats: dict = None,
                            default_stats=None, silent=False, flush: bool = True, **_key_modes) -> None:
        """
        logs the statistical properties of the stored metrics, and clears the `summary_cache` if under `tiled` mode,
        and keeps the data otherwise (under `rolling` mode).

        To enable explicit mode without specifying *only_keys, set
        `get_only` to True

        Modes for the Statistics:
        =========================

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
        cache = cache or self.summary_cache
        summary = cache.summarize(key_stats=key_stats, default_stats=default_stats, **_key_modes)
        if key_values:
            summary.update(key_values)
        self.log_metrics(metrics=summary, silent=silent, flush=flush)

    def log(self, *args, metrics=None, silent=False, sep=" ", end="\n", flush=None,
            **_key_values) -> None:
        """
        log dictionaries of data, key=value pairs at step == step.

        logs *argss as line and kwargs as key / value pairs

        :param args: (str) strings or objects to be printed.
        :param metrics: (dict) a dictionary of key/value pairs to be saved in the key_value_cache
        :param sep: (str) separator between the strings in *args
        :param end: (str) string to use for the end of line. Default to "\n"
        :param silent: (boolean) whether to also print to stdout or just log to file
        :param flush: (boolean) whether to flush the text logs
        :param kwargs: key/value arguments
        :return:
        """
        if args:  # do NOT print the '\n' if args is empty in call. Different from the signature of the print function.
            self.log_line(*args, sep=sep, end=end, flush=False)
        if metrics:
            _key_values.update(metrics)
        self.log_metrics(metrics=_key_values, silent=silent)
        if flush:
            self.flush()

    metric_filename = "metrics.pkl"
    log_filename = "outputs.log"

    def flush_metrics(self, cache=None, filename=None):
        key_values = (cache or self.key_value_cache).pop_all()
        filename = filename or self.metric_filename
        output = self.print_helper.format_tabular(key_values, self.do_not_print)
        self.log_text(output, silent=False)  # not buffered
        self.client.log(key=os.path.join(self.prefix, filename), data=key_values)
        self.do_not_print.reset()

    def flush(self):
        self.log_metrics_summary(flush=False)
        self.flush_metrics()
        self.flush_print_buffer()

    def upload_file(self, file_path: str = None, target_folder: str = "files") -> None:
        """
        uploads a file (through a binary byte string) to a target_folder. Default
        target is "files"

        :param file_path: the path to the file to be uploaded
        :param target_folder: the target folder for the file, preserving the filename of the file.
        :return: None
        """
        from pathlib import Path
        bytes = Path(file_path).read_bytes()
        basename = os.path.basename(file_path)
        self.client.log_buffer(key=os.path.join(target_folder, basename), buf=bytes)

    def upload_dir(self, dir_path, target_folder='', excludes=tuple(), gzip=True, unzip=False):
        """log a directory, or upload an entire directory."""
        raise NotImplementedError

    def log_images(self, stack, key, n_rows=None, n_cols=None, cmap=None, normalize=None):
        """Log images as a composite of a grid. Images input as a 4-D stack.

        :param stack: Size(n, w, h, c)
        :param key: the filename for the composite image.
        :param n_rows: number of rows
        :param n_cols: number of columns
        :param cmap: OneOf([str, matplotlib.cm.ColorMap])
        :param normalize: defaul None. OneOf[None, 'indivisual', 'row', 'column', 'grid']. Only 'grid' and
                          'individual' are implemented.
        :return: None
        """
        stack = stack if hasattr(stack, 'dtype') else np.array(stack)

        n_cols = n_cols or len(stack)
        n_rows = n_rows or 1

        if np.issubdtype(stack.dtype, np.uint8):
            pass
        elif len(stack.shape) == 3:
            from matplotlib import cm
            map_fn = cm.get_cmap(cmap or 'Greys')
            # todo: this needs to happen for each individual imagedata
            if normalize is None:
                pass
            elif normalize == 'individual':
                r = stack.max(axis=1) - stack.min(axis=1)
                stack = (stack - stack.min(axis=1)[:, :, None]) / np.select([r != 0], [r], 1)[:, :, None]
            elif normalize == 'grid':
                stack = (stack - stack.min()) / (stack.max() - stack.min() or 1)
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
        composite = np.ones([h * n_rows, w * n_cols, *c], dtype='uint8')
        for i in range(n_rows):
            for j in range(n_cols):
                k = i * n_cols + j
                if k >= n:
                    break
                # todo: remove last index
                composite[i * h: i * h + h, j * w: j * w + w] = stack[k]

        self.client.send_image(key=os.path.join(self.prefix, key), data=composite)

    def log_image(self, image, key: str, cmap=None, normalize=None):
        """Log a single image.

        :param image: numpy object Size(w, h, 3)
        :param key: example: "figures/some_fig_name.png", the file key to which the
            image is saved.
        """
        self.log_images([image], key, n_rows=1, n_cols=1, cmap=cmap, normalize=normalize)

    def log_video(self, frame_stack, key, format=None, fps=20, **imageio_kwargs):
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

        filename = os.path.join(self.prefix, key)
        import tempfile, imageio
        with tempfile.NamedTemporaryFile(suffix=f'.{format}') as ntp:
            try:
                imageio.mimsave(ntp.name, frame_stack, format=format, fps=fps, **imageio_kwargs)
            except imageio.core.NeedDownloadError:
                imageio.plugins.ffmpeg.download()
                imageio.mimsave(ntp.name, frame_stack, format=format, fps=fps, **imageio_kwargs)
            ntp.seek(0)
            self.client.log_buffer(key=filename, buf=ntp.read())

    def log_pyplot(self, path="plot.png", fig=None, format=None, **kwargs):
        """
        Now also handles pdf and svg file formats!

        ref: see this link https://stackoverflow.com/a/8598881/1560241

        :param path:
        :param fig:
        :param format:
        :param kwargs:
        :return:
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

        path = os.path.join(self.prefix, path)
        self.client.log_buffer(path, buf.read())
        return path

    def savefig(self, key, fig=None, format=None, **kwargs):
        """ This method emulates `matplotlib.pyplot.savefig` method. Requires key string for the file name. """
        self.log_pyplot(path=key, fig=fig, format=format, **kwargs)

    def save_module(self, module, path="weights.pkl", chunk=100_000, show_progress=False):
        """
        Save torch module. Overwrites existing file.

        When the model is large, this function uploads the weight dictionary (state_dict) in
        chunks. You can specify the size for the chunks, measured in number of tensors.

        The conversion convention for the upload chunks is roughly 32bit, or 8 bytes for each
        `np.float32` entry. so the upload size for chunk = 100,000 is roughly

            100_000 * 8 * <base56 encoding ration> ~ 960k.

        :param module: the PyTorch module to be saved.
        :param path: filename to which we save the module.
        :param chunk: chunk size for the tensor, measured in number of tensor entries.
        :param show_progress: boolean flag, default to False. Displays a progress bar when trueful. If the type
            is string, then use this as the description for the progress bar.

            Default progress description text is the file key to which we are writing.

        :return: None
        """
        # todo: raise error if particular weight file is too big
        _ = module.state_dict().items()
        if show_progress:
            from tqdm import tqdm
            _ = tqdm(_, desc=show_progress if isinstance(show_progress, str) else path[-24:])

        size, data_chunk = 0, {}
        for k, _v in _:
            v = _v.detach().cpu().numpy()
            assert v.size < chunk, "individual weight tensors need to be smaller than the chunk size"
            if size + v.size > chunk:
                self.log_data(data=data_chunk, path=path, overwrite=False if size else True)
                size = v.size
                data_chunk = {k: v}
            else:
                size += v.size
                data_chunk[k] = v

        self.log_data(data=data_chunk, path=path, overwrite=False)
        # data = {k: v.cpu().detach().numpy() for k, v in module.state_dict().items()}
        # self.log_data(data=data, path=path, overwrite=True)

    def load_module(self, module, path="weights.pkl", stream=True):
        """
        Load torch module from file.

        :param module: target torch module you want to load
        :param path: the weight file containing the weights
        :return: None
        """
        import torch
        d = {}
        for chunk in (self.iload_pkl if stream else self.load_pkl)(path):
            d.update(chunk)

        assert d, f"the datafile can not be empty: [d == {{{d.keys()}...}}]"

        module.load_state_dict({
            k: torch.tensor(d[k], dtype=p.dtype).to(p.device)
            for k, p in module.state_dict().items()
        })

    def save_modules(self, path="modules.pkl", modules=None, **_modules):
        """
        Save torch modules in a dictionary, keyed by the keys.

        *Overwrites existing file*.

        This function is only used to save a collection of modules that can be
        sent over in a single post request. When the modules are large, we use
        the `logger.save_module` method, to send chunks of weight tensors one-
        by-one.

        :param path: filename to be saved.
        :param modules: dictionary/namespace for the modules.
        :param _modules: key/value pairs for different modules to be saved
        :return: None
        """
        _modules.update(modules or {})
        data = {name: {k: v.cpu().detach().numpy() for k, v in module.state_dict().items()}
                for name, module in _modules.items()}
        self.log_data(data=data, path=path, overwrite=True)

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
        if keys is None:
            keys = [v.name for v in variables]
        assert len(keys) == len(variables), 'the keys and the variables have to be the same length.'
        import tensorflow as tf
        sess = tf.get_default_session()
        vals = sess.run(variables)
        weight_dict = {k.split(":")[0]: v for k, v in zip(keys, vals)}
        logger.log_data(weight_dict, path, overwrite=True)

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
        import tensorflow as tf
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

    def load_file(self, key):
        """ return the binary stream, most versatile.

        todo: check handling of line-separated files

        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        :param key: a path string
        :return: a tuple of each one of the data chunck logged into the file.
        """
        return self.client.read(os.path.join(self.prefix, key))

    def load_text(self, key):
        """ return the text content of the file (in a single chunk)

        todo: check handling of line-separated files

        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        :param key: a path string
        :return: a tuple of each one of the data chunck logged into the file.
        """
        return self.client.read_text(os.path.join(self.prefix, key))

    def load_pkl(self, key, start=None, stop=None):
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

        :param key: a path string
        :param start: Starting index for the chunks None means from the beginning.
        :param stop: Stop index for the chunks. None means to the end of the file.
        :return: a tuple of each one of the data chunck logged into the file.
        """
        path = os.path.join(self.prefix, key)
        return self.client.read_pkl(path, start, stop)

    def iload_pkl(self, key):
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
        :return: a iterator.
        """
        path = os.path.join(self.prefix, key)
        i = 0
        while True:
            chunks = self.client.read_pkl(path, i, i + 1)
            i += 1
            if not chunks:
                break
            yield from chunks

    def load_np(self, key):
        """ load a np file

        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        :param key: a path string
        :return: a tuple of each one of the data chunck logged into the file.
        """
        return self.client.read_np(os.path.join(self.prefix, key))

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

    def log_json(self):
        raise NotImplementedError

    def log_line(self, *args, sep=' ', end='\n', flush=True, file=None, color=None):
        """
        this is similar to the print function. It logs *args with a default EOL postfix in the end.

        .. code:: python

            n = 10
            logger.log_line("mary", "has", n, "sheep.", color="green")

        ::

            >>> "mary has 10 sheep" (colored green)

        :param *args: List of object to be converted to string and printed out.
        :param sep: Same as the `sep` kwarg in regular print statements
        :param end: Same as the `end` kwarg in regular print statements
        :param flush: bool, whether the output is flushed. Default to True
        :param file: file object to whitch the line is written
        :param color: str, color of the line
        :return:
        """
        text = sep.join([str(a) for a in args]) + end
        if color:
            from termcolor import colored
            text = colored(text, color)
        self.print_buffer += text
        if flush or file or len(self.print_buffer) > self.print_buffer_size:
            self.flush_print_buffer(file=file)

    def flush_print_buffer(self, file=None):
        if self.print_buffer:
            self.log_text(self.print_buffer, filename=file, silent=False)
        self.print_buffer = ""

    def log_text(self, text: str = None, filename=None, silent=True):
        """
        logging and printing a string object.

        This does not log to the buffer. It calls the low-level log_text method right away
        without buffering.

        :param text:
        :param filename:
        :param silent:
        :return:
        """
        filename = filename or self.log_filename
        if text is not None:
            self.client.log_text(key=os.path.join(self.prefix, filename), text=text)
            if not silent:
                print(text, end="")

    def glob(self, query, wd=None, recursive=True, start=None, stop=None):
        """
        Globs files under the work directory (`wd`). Note that `wd` affects the file paths
        being returned. The default is the current logging prefix. Use absolute path (with
        a leanding slash (`/`) to escape the logging prefix. Use two leanding slashes for
        the absolute path in the host for the logging server.

        :param query:
        :param wd: defaults to the current prefix. When trueful values are given, uses:
            > wd = os.path.join(self.prefix, wd)

            if you want root of the logging server instance, use abs path headed by `/`.
            If you want root of the server file system, double slash: `//home/directory-name-blah`.

        :param recursive:
        :param start:
        :param stop:
        :return:
        """
        wd = os.path.join(self.prefix, wd or "")
        return self.client.glob(query, wd=wd, recursive=recursive, start=start, stop=stop)


logger = ML_Logger()
