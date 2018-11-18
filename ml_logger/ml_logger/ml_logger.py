import os
import numpy as np
from collections import OrderedDict, Sequence
from datetime import datetime
from io import BytesIO
from numbers import Number
from typing import Union, Any

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


ML_DASH = "http://{host}:3000/experiments/ins-runs/{prefix}"


# noinspection PyPep8Naming
class ML_Logger:
    logger = None
    log_directory = None

    prefix = ""
    print_buffer = ""  # is okay b/c strings are immutable in python

    # noinspection PyInitNewSignature
    def __init__(self, log_directory: str = None, prefix=None, buffer_size=2048, max_workers=5,
                 summary_cache_opts: dict = None):
        """ Configuration function for the logger.

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
        :param buffer_size: The string buffer size for the print buffer.
        :param max_workers: the number of request-session workers for the async http requests.
        """
        # self.summary_writer = tf.summary.FileWriter(log_directory)
        self.step = None
        self.duplex = None
        self.timestamp = None
        self.print_buffer_size = buffer_size
        self.key_value_cache = KeyValueCache()
        self.summary_cache = SummaryCache(**(summary_cache_opts or {}))
        self.do_not_print = DefaultSet("__timestamp")
        if prefix is not None:
            assert not os.path.isabs(prefix), "prefix can not start with `/` because it is relative to `log_directory`."
            self.prefix = prefix

        self.print_helper = PrintHelper()
        # todo: add https support
        if log_directory:
            self.logger = LogClient(url=log_directory, max_workers=max_workers)
            self.log_directory = log_directory
            # register experiment
            if log_directory.startswith("http://"):
                host, port = log_directory[7:].split(":")
                run_info = dict(dashboard=ML_DASH.format(host=host, prefix=self.prefix))
                self.log_params(run=run_info)

            # self.log_caller()
            # self.log_revision()

    configure = __init__

    def log_caller(self, context=5):
        """
        logs information of the caller's stack (module, filename etc)
        :return:
        """
        import inspect
        caller_info = None
        for frame, filename, lineno, func_name, code_context, index in inspect.stack(context=context):
            module = inspect.getmodule(frame)
            if module.__name__ != "ml_logger.ml_logger":
                outer_frame, *_ = inspect.getouterframes(frame, 1)[0]
                if not caller_info:
                    caller_info = dict(name=func_name, context="".join(code_context), filename=filename, line=lineno)
                else:
                    try:
                        from textwrap import dedent
                        caller = frame.f_locals[caller_info['name']]
                        caller_info['doc'] = dedent(caller.__doc__)
                        break
                    except Exception as e:
                        self.log_line(e)

        self.log_params(caller_info=caller_info)

    def log_revision(self, silent_diff=True):
        rev = dict(hash=logger.__head__, branch=logger.__current_branch__)
        self.log_params(revision=rev)
        self.diff(silent=silent_diff)

    # timing functions
    def split(self):
        """
        returns a datetime object. You can get integer seconds and miliseconds (both int) from it.
        Note: This is Not idempotent, which is why it is not a property.

        :return: float (seconds/miliseconds)
        """
        new_tic = self.now
        try:
            dt = new_tic - self._tic
            self._tic = new_tic
            return dt.total_seconds()
        except AttributeError:
            self._tic = new_tic
            return None

    @property
    def now(self, fmt=None):
        from datetime import datetime
        now = datetime.now()
        return now.strftime(fmt) if fmt else now

    def diff(self, diff_directory=".", diff_filename="index.diff", silent=False):
        """
        example usage: M.diff('.')
        :param diff_directory: The root directory to call `git diff`.
        :param log_directory: The overriding log directory to save this diff index file
        :param diff_filename: The filename for the diff file.
        :return: None
        """
        import subprocess
        try:
            cmd = f'cd "{os.path.realpath(diff_directory)}" && git add . && git --no-pager diff HEAD'
            if not silent: self.log_line(cmd)
            p = subprocess.check_output(cmd, shell=True)  # Save git diff to experiment directory
            self.log_text(p.decode('utf-8').strip(), diff_filename, silent=silent)
        except subprocess.CalledProcessError as e:
            self.log_line("not storing the git diff due to {}".format(e))

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
        returns the git revision hash of the branch that you pass in.
        full reference here: https://stackoverflow.com/a/949391
        the `show-ref` and the `for-each-ref` commands both show a list of refs. We only need to get the
        ref hash for the revision, not the entire branch of by tag.
        """
        import subprocess
        try:
            cmd = ['git', 'rev-parse', branch]
            p = subprocess.check_output(cmd)  # Save git diff to experiment directory
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
        raise NotImplemented

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
                    return self.logger.ping(self.prefix, statuses[-1])
                else:
                    return self.logger.ping(self.prefix, "running")

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
        self.logger._delete(abs_path)

    def log_params(self, path="parameters.pkl", **kwargs):
        from termcolor import colored as c
        key_width = 20
        value_width = 20

        _kwargs = {}
        table = []
        for n, (title, section_data) in enumerate(kwargs.items()):
            table.append('═' * (key_width) + ('═' if n == 0 else '╧') + '═' * (value_width))
            table.append(c('{:^{}}'.format(title, key_width), 'yellow') + "")
            table.append('─' * (key_width) + "┬" + '─' * (value_width))
            if not hasattr(section_data, 'items'):
                table.append(section_data)
                _kwargs[title] = metrify(section_data)
            else:
                _param_dict = {}
                for key, value in section_data.items():
                    _param_dict[key] = metrify(value.v if type(value) is Color else value)
                    value_string = str(value)
                    table.append('{:^{}}'.format(key, key_width) + "│" + '{:<{}}'.format(value_string, value_width))
                _kwargs[title] = _param_dict

        if "n" in locals():
            table.append('═' * key_width + '╧' + '═' * value_width)

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
        self.logger.log(**kwargs)

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
        timestamp = np.datetime64(datetime.now())
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
        timestamp = np.datetime64(datetime.now())
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
        output = self.print_helper.format_row_table(_, do_not_print_list=self.do_not_print)
        (print if print_only else self.log_line)(output)

    def log_metrics_summary(self, key_values: dict = None, cache: SummaryCache = None, key_modes: dict = None,
                            silent=False, flush: bool = True, **_key_modes) -> None:
        """
        logs the statistical properties of the stored metrics, and clears the `summary_cache` if under `tiled` mode,
        and keeps the data otherwise (under `rolling` mode).

        :param key_values: extra key (and values) to log together with summary such as `timestep`, `epoch`, etc.
        :param cache: (dict) An optional cache object from which the summary is made.
        :param key_modes: (dict) a dictionary for the key and the statistic modes to be returned.
        :param flush: (bool) flush the key_value cache if trueful.
        :param _key_modes: (**) key value pairs, as a short hand for the key_modes dictionary.
        :return: None
        """
        cache = cache or self.summary_cache
        summary = cache.summarize(key_modes=key_modes, **_key_modes)
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
        self.logger.log(key=os.path.join(self.prefix, filename), data=key_values)
        self.do_not_print.reset()

    def flush(self):
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
        self.logger.log_buffer(key=os.path.join(target_folder, basename), buf=bytes)

    def upload_dir(self, dir_path, target_folder='', excludes=tuple(), gzip=True, unzip=False):
        """log a directory, or upload an entire directory."""

    def log_images(self, key, stack, ncol=5, nrows=2, namespace="image", fstring="{:04d}.png"):
        """note: might make sense to push the operation to the server instead.
        logs a stack of images from a tensor object. Could also be part of the server code.

        update: client-side makes more sense, less data to send.
        """
        pass

    def log_image(self, image, key):
        """
        DONE: IMPROVE API. I'm not a big fan of this particular api.
        Logs an image via the summary writer.
        TODO: add support for PIL images etc.
        reference: https://gist.github.com/gyglim/1f8dfb1b5c82627ae3efcfbbadb9f514

        Because the image keys are passed in as variable keys, it is not as easy to use a string literal
        for the file name (key). as a result, we generate the numerated filename for the user.

        value: numpy object Size(w, h, 3)
        """
        filename = os.path.join(self.prefix, key)
        self.logger.send_image(key=filename, data=image)

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
            self.logger.log_buffer(key=filename, buf=ntp.read())

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
        self.logger.log_buffer(path, buf.read())
        return path

    def savefig(self, key, fig=None, format=None, **kwargs):
        """ This method emulates `matplotlib.pyplot.savefig` method. Requires key string for the file name. """
        self.log_pyplot(path=key, fig=fig, format=format, **kwargs)

    def save_module(self, module, path="weights.pkl"):
        """
        log torch module

        todo: log tensorflow modules.

        :param module: the PyTorch module to be saved.
        :param path: filename to which we save the module.
        :return:
        """
        # todo: this is torch-specific code. figure out a better way.
        ps = {k: v.cpu().detach().numpy() for k, v in module.state_dict().items()}
        self.log_data(path=path, data=ps, overwrite=True)

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
        import os
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

        :param key:
        :return:
        """
        return self.logger.read(os.path.join(self.prefix, key))

    def load_pkl(self, key):
        """
        load a pkl file (as a tuple)

        :param key:
        :return:
        """
        return self.logger.read_pkl(os.path.join(self.prefix, key))

    def load_np(self, key):
        """ load a np file

        :param key:
        :return:
        """
        return self.logger.read_np(os.path.join(self.prefix, key))

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

    def log_line(self, *args, sep=' ', end='\n', flush=True, file=None):
        """
        this is similar to the print function. It logs *args with a default EOL postfix in the end.

        :param args:
        :param sep:
        :param end:
        :param flush:
        :param file:
        :return:
        """
        text = sep.join([str(a) for a in args]) + end
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
            self.logger.log_text(key=os.path.join(self.prefix, filename), text=text)
            if not silent:
                print(text, end="")


logger = ML_Logger()
