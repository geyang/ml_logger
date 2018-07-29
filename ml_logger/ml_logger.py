from io import BytesIO

import os
from datetime import datetime

from typing import Union, Callable, Any
from collections import OrderedDict, deque
from itertools import zip_longest

from ml_logger.log_client import LogClient
from termcolor import colored as c
import numpy as np


class Stream:
    def __init__(self, len=100):
        self.d = deque(maxlen=len)

    def append(self, d):
        self.d.append(d)

    @property
    def latest(self):
        return self.d[-1]

    @property
    def mean(self):
        try:
            return np.mean(self.d)
        except ValueError:
            return None

    @property
    def max(self):
        try:
            return np.max(self.d)
        except ValueError:
            return None

    @property
    def min(self):
        try:
            return np.min(self.d)
        except ValueError:
            return None


class Color:
    # noinspection PyInitNewSignature
    def __init__(self, value, color=None, formatter: Union[Callable[[Any], Any], None] = lambda v: v):
        self.value = value
        self.color = color
        self.formatter = formatter

    def __str__(self):
        return str(self.formatter(self.value)) if callable(self.formatter) else str(self.value)

    def __len__(self):
        return len(str(self.value))

    def __format__(self, format_spec):
        if self.color in [None, 'default']:
            return self.formatter(self.value).__format__(format_spec)
        else:
            return c(self.formatter(self.value).__format__(format_spec), self.color)


def percent(v):
    return '{:.02%}'.format(round(v * 100))


def ms(v):
    return '{:.1f}ms'.format(v * 1000)


def sec(v):
    return '{:.3f}s'.format(v)


def default(value, *args, **kwargs):
    return Color(value, 'default', *args, **kwargs)


def red(value, *args, **kwargs):
    return Color(value, 'red', *args, **kwargs)


def green(value, *args, **kwargs):
    return Color(value, 'green', *args, **kwargs)


def gray(value, *args, **kwargs):
    return Color(value, 'gray', *args, **kwargs)


def grey(value, *args, **kwargs):
    return Color(value, 'gray', *args, **kwargs)


def yellow(value, *args, **kwargs):
    return Color(value, 'yellow', *args, **kwargs)


def brown(value, *args, **kwargs):
    return Color(value, 'brown', *args, **kwargs)


class ML_Logger:
    logger = None
    log_directory = None

    @property
    def now(self, fmt=None):
        from datetime import datetime
        now = datetime.now()
        # now.strftime("%Y-%m-%d-%H-%M-%S-%f")
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
            cmd = f'cd "{os.path.realpath(diff_directory)}" && git add . && git --no-pager diff --staged'
            self.print(cmd)
            p = subprocess.check_output(cmd, shell=True)  # Save git diff to experiment directory
            self.log_text(p.decode('utf-8'), diff_filename, silent=silent)
        except subprocess.CalledProcessError as e:
            self.print("not storing the git diff due to {}".format(e))

    def diff_file(self, path, silent=False):
        raise NotImplemented

    # noinspection PyInitNewSignature
    def __init__(self, log_directory: str = None, prefix="", buffer_size=2048, max_workers=5):
        """
        :param log_directory: Overloaded to use either
            - file://some_abs_dir
            - http://19.2.34.3:8081
            - /tmp/some_dir
        :param prefix: The directory relative to those above
            - prefix: causal_infogan => /tmp/some_dir/causal_infogan
            - prefix: "" => /tmp/some_dir
        """
        # self.summary_writer = tf.summary.FileWriter(log_directory)
        self.step = None
        self.timestamp = None
        self.data = OrderedDict()
        self.flush()
        self.print_buffer_size = buffer_size
        self.do_not_print_list = set()
        assert not os.path.isabs(prefix), "prefix can not start with `/`"
        self.prefix = prefix

        # todo: add https support
        if log_directory:
            self.logger = LogClient(url=log_directory, max_workers=max_workers)
            self.log_directory = log_directory

    configure = __init__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.summary_writer.close()
        # todo: wait for logger to finish upload in async mode.
        self.flush()

    def log_params(self, path="parameters.pkl", **kwargs):
        key_width = 30
        value_width = 20

        table = []
        for n, (title, section_data) in enumerate(kwargs.items()):
            table.append((title, ""))
            self.print('═' * (key_width + 1) + ('═' if n == 0 else '╧') + '═' * (value_width + 1))
            self.print(c('{:^{}}'.format(title, key_width), 'yellow'))
            self.print('─' * (key_width + 1) + "┬" + '─' * (value_width + 1))
            for key, value in section_data.items():
                value_string = str(value)
                table.append((key, value_string))
                self.print('{:^{}}'.format(key, key_width), "│",
                           '{:<{}}'.format(value_string, value_width))

        if "n" in locals():
            self.print('═' * (key_width + 1) + ('═' if n == 0 else '╧') + '═' * (value_width + 1))

        # todo: add logging hook
        # todo: add yml support
        self.log_data(path=path, data=kwargs)

    def log_data(self, path="data.pkl", data=None):
        self.logger.log(key=os.path.join(self.prefix or "", path), data=data)

    def log_keyvalue(self, key: str, value: Any, step: Union[int, Color] = None, silent=False) -> None:
        if self.step != step and step is not None:
            self.flush()
            self.step = step

        self.timestamp = np.datetime64(datetime.now())

        if silent:
            self.do_not_print_list.update([key])

        if step is None and self.step is None and key in self.data:
            self.flush()

        if key in self.data:
            if type(self.data) is list:
                self.data[key].append(value.value if type(value) is Color else value)
            else:
                self.data[key] = [self.data[key]] + [value.value if type(value) is Color else value]
        else:
            self.data[key] = value.value if type(value) is Color else value

    def log(self, *dicts, step: Union[int, Color] = None, silent=False, **kwargs) -> None:
        """
        log dictionaries of data, key=value pairs at step == step.

        :param step: the global step, be it the global timesteps or the epoch step
        :param dicts: a dictionary or a list of dictionaries of key/value pairs, allowing more flexible key name with '/' etc.
        :param silent: Bool, log but do not print. To keep the standard out silent.
        :param kwargs: key/value arguments.
        :return:
        """
        if self.step != step and step is not None:
            self.flush()
            self.step = step

        self.timestamp = np.datetime64(datetime.now())

        data_dict = {}
        for d in dicts:
            data_dict.update(d)
        data_dict.update(kwargs)

        if silent:
            self.do_not_print_list.update(data_dict.keys())

        # todo: add logging hook
        for key, v in data_dict.items():
            if key in self.data:
                if type(self.data) is list:
                    self.data[key].append(v.value if type(v) is Color else v)
                else:
                    self.data[key] = [self.data[key], v.value if type(v) is Color else v]
            else:
                self.data[key] = v.value if type(v) is Color else v

    @staticmethod
    def _tabular(data, fmt=".3f", do_not_print_list=tuple(), min_key_width=20, min_value_width=20):
        keys = [k for k in data.keys() if k not in do_not_print_list]
        if len(keys) > 0:
            max_key_len = max([min_key_width] + [len(k) for k in keys])
            max_value_len = max([min_value_width] + [len(str(data[k])) for k in keys])
            output = None
            for k in keys:
                v = f"{data[k]:{fmt}}"
                if output is None:
                    output = "╒" + "═" * max_key_len + "╤" + "═" * max_value_len + "╕\n"
                else:
                    output += "├" + "─" * max_key_len + "┼" + "─" * max_value_len + "┤\n"
                if k not in do_not_print_list:
                    k = k.replace('_', " ")
                    v = "NA" if v is None else v  # for NoneTypes which doesn't have __format__ method
                    output += f"│{k:^{max_key_len}}│{v:^{max_value_len}}│\n"
            output += "╘" + "═" * max_key_len + "╧" + "═" * max_value_len + "╛\n"
            return output

    @staticmethod
    def _row_table(data, fmt=".3f", do_not_print_list=tuple(), min_column_width=5):
        """applies to metrics keys with multiple values"""
        keys = [k for k in data.keys() if k not in do_not_print_list]
        output = ""
        if len(keys) > 0:
            values = [values if type(values) is list else [values] for values in data.values()]
            max_key_width = max([min_column_width] + [len(k) for k in keys])
            max_value_len = max([min_column_width] + [len(f"{v:{fmt}}") for d in values for v in d])
            max_width = max(max_key_width, max_value_len)
            output += '|'.join([f"{key.replace('-', ' '):^{max_width}}" for key in keys]) + "\n"
            output += "┼".join(["─" * max_width] * len(keys)) + "\n"
            for row in zip_longest(*values):
                output += '|'.join([f"{value:^{max_width}{fmt}}" for value in row]) + "\n"
            return output

    def flush(self, file_name="metrics.pkl", fmt=".3f"):
        if self.data:
            try:
                output = self._tabular(self.data, fmt, self.do_not_print_list)
            except Exception as e:
                print(e)
                output = self._row_table(self.data, fmt, self.do_not_print_list)
            self.print(output)
            self.logger.log(key=os.path.join(self.prefix or "", file_name or "metrics.pkl"),
                            data=dict(_step=self.step, _timestamp=str(self.timestamp), **self.data))
            self.data.clear()
            self.do_not_print_list.clear()
            
        self.print_flush()

    def log_file(self, file_path, namespace='files', silent=True):
        # todo: make it possible to log multiple files
        # todo: log dir
        from pathlib import Path
        content = Path(file_path).read_text()
        basename = os.path.basename(file_path)
        self.log_text(content, filename=os.path.join(namespace, basename), silent=silent)

    def log_dir(self, dir_path, namespace='', excludes=tuple(), silent=True):
        """log a directory"""

    def log_images(self, key, stack, ncol=5, nrows=2, namespace="image", fstring="{:04d}.png"):
        """note: might makesense to push the operation to the server instead.
        logs a stack of images from a tensor object. Could also be part of the server code.

        update: client-side makes more sense, less data to send.
        """
        pass

    def log_image(self, image, key, namespace="images", format="png"):
        """
        DONE: IMPROVE API. I'm not a big fan of this particular api.
        Logs an image via the summary writer.
        TODO: add support for PIL images etc.
        reference: https://gist.github.com/gyglim/1f8dfb1b5c82627ae3efcfbbadb9f514

        Because the image keys are passed in as variable keys, it is not as easy to use a string literal
        for the file name (key). as a result, we generate the numerated filename for the user.

        value: numpy object Size(w, h, 3)

        """
        if format:
            key += "." + format

        filename = os.path.join(self.prefix or "", namespace, key)
        self.logger.send_image(key=filename, data=image)

    def log_video(self, frame_stack, key, namespace='videos', format=None, fps=20, macro_block_size=None,
                  **imageio_kwargs):
        """
        Let's do the compression here. Video frames are first written to a temporary file
        and the file containing the compressed data is sent over as a file buffer.
        
        Save a stack of images to

        :param frame_stack:
        :param key:
        :param namespace:
        :param fmt:
        :param ext:
        :param step:
        :param imageio_kwargs:
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

        filename = os.path.join(self.prefix or "", namespace, key)

        import tempfile, imageio
        with tempfile.NamedTemporaryFile(suffix=f'.{format}') as ntp:
            imageio.mimwrite(ntp.name, frame_stack, format=format, fps=fps, macro_block_size=macro_block_size,
                             **imageio_kwargs)
            ntp.seek(0)
            self.logger.log_buffer(key=filename, buf=ntp.read())

    def log_pyplot(self, key="plot", fig=None, format=None, namespace="plots", **kwargs):
        """
        does not handle pdf and svg file formats. A big annoying.

        ref: see this link https://stackoverflow.com/a/8598881/1560241

        :param key:
        :param fig:
        :param namespace:
        :param fmt:
        :param step:
        :return:
        """
        # can not simplify the logic, because we can't pass the filename to pyplot. A buffer is passed in instead.
        if format:  # so allow key with dots in it: metric_plot.text.plot + ".png". Because user intention is clear
            key += "." + format
        else:
            _, format = os.path.splitext(key)
            if format:
                format = format[1:]  # to get rid of the "." at the begining of '.svg'.
            else:
                format = "png"
                key += "." + format

        if fig is None:
            from matplotlib import pyplot as plt
            fig = plt.gcf()

        buf = BytesIO()
        fig.savefig(buf, format=format, **kwargs)
        buf.seek(0)

        path = os.path.join(self.prefix or "", namespace, key)
        self.logger.log_buffer(path, buf.read())
        return key

    def savefig(self, key, fig=None, format=None, **kwargs):
        """
        This one overrides the namespace default of log_pyplot.
        This way, the key behave exactly the same way pyplot.savefig behaves.

        default plotting file name is plot.png under the current directory


        """
        self.log_pyplot(key=key, fig=fig, format=format, namespace="", **kwargs)

    def log_module(self, namespace="modules", fmt="04d", step=None, **kwargs):
        """
        log torch module

        todo: log tensorflow modules.

        :param fmt: 03d, 0.2f etc. The formatting string for the step key.
        :param step:
        :param namespace:
        :param kwargs:
        :return:
        """
        if self.step != step and step is not None:
            self.flush()
            self.step = step

        for k, m in kwargs.items():
            # todo: this is torch-specific code. figure out a better way.
            ps = {k: v.cpu().detach().numpy() for k, v in m.state_dict().items()},
            # we use the number first file names to help organize modules by epoch.
            path = os.path.join(namespace, f'{k}.pkl' if self.step is None else f'{step:{fmt}}_{k}.pkl')
            self.log_data(path=path, data=ps)

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

    def print(self, *args, sep=' ', end='\n', silent=False):
        text = sep.join([str(a) for a in args]) + end
        try:
            self.print_buffer += text
        except:
            self.print_buffer = text
        if not silent:
            print(*args, sep=sep, end=end)
        if len(self.print_buffer) > self.print_buffer_size:
            self.print_flush()

    def print_flush(self):
        try:
            text = self.print_buffer
        except:
            text = ""
        self.print_buffer = ""
        if text:
            self.log_text(text, silent=True)

    def log_text(self, text, filename="text.log", silent=False):
        # todo: consider adding step to this
        if not silent:
            print(text)
        self.logger.log_text(key=os.path.join(self.prefix or "", filename), text=text)


logger = ML_Logger()
