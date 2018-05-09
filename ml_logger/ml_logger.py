import os
from datetime import datetime

from typing import Union, Callable, Any
from collections import OrderedDict, deque

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

    # noinspection PyInitNewSignature
    def __init__(self, log_directory: str = None, prefix=""):
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
        self.do_not_print_list = set()
        assert not os.path.isabs(prefix), "prefix can not start with `/`"
        self.prefix = prefix

        # todo: add https support
        if log_directory:
            self.logger = LogClient(url=log_directory)
            self.log_directory = log_directory

    configure = __init__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.summary_writer.close()
        # todo: wait for logger to finish upload in async mode.
        self.flush()

    def log_params(self, **kwargs):
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
        self.logger.log(key=os.path.join(self.prefix or "", "parameters.pkl"), data=kwargs)

    def log_keyvalue(self, step: Union[int, Color], key: str, value: Any, silent=False) -> None:
        if self.step != step and self.step is not None:
            self.flush()
        self.step = step
        self.timestamp = np.datetime64(datetime.now())

        if silent:
            self.do_not_print_list.update([key])

        # todo: add logging hook
        self.data[key] = value.value if type(value) is Color else value

    def log(self, step: Union[int, Color], *dicts, silent=False, **kwargs) -> None:
        """
        :param step: the global step, be it the global timesteps or the epoch step
        :param dicts: a dictionary of key/value pairs, allowing more flexible key name with '/' etc.
        :param silent: Bool, log but do not print. To keep the standard out silent.
        :param kwargs: key/value arguments.
        :return:
        """
        if self.step != step and self.step is not None:
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
            self.data[key] = v.value if type(v) is Color else v

    def flush(self, min_key_width=20, min_value_width=20):
        if not self.data:
            return

        keys = [k for k in self.data.keys() if k not in self.do_not_print_list]

        if len(keys) > 0:
            max_key_len = max([min_key_width] + [len(k) for k in keys])
            max_value_len = max([min_value_width] + [len(str(self.data[k])) for k in keys])
            output = None
            for k in keys:
                v = str(self.data[k])
                if output is None:
                    output = "╒" + "═" * max_key_len + "╤" + "═" * max_value_len + "╕\n"
                else:
                    output += "├" + "─" * max_key_len + "┼" + "─" * max_value_len + "┤\n"
                if k not in self.do_not_print_list:
                    k = k.replace('_', " ")
                    v = "None" if v is None else v  # for NoneTypes which doesn't have __format__ method
                    output += "│{:^{}}│{:^{}}│\n".format(k, max_key_len, v, max_value_len)
            output += "╘" + "═" * max_key_len + "╧" + "═" * max_value_len + "╛\n"
            self.print(output, end="")

        self.logger.log(key=os.path.join(self.prefix or "", "data.pkl"),
                        data=dict(_step=self.step, _timestamp=str(self.timestamp), **self.data))
        self.data.clear()
        self.do_not_print_list.clear()

    def log_image(self, step, namespace="images", **kwargs):
        """Logs an image via the summary writer.
        TODO: add support for PIL images etc.
        reference: https://gist.github.com/gyglim/1f8dfb1b5c82627ae3efcfbbadb9f514
        """
        if self.step != step and self.step is not None:
            self.flush()
        self.step = step
        self.timestamp = np.datetime64(datetime.now())

        # todo: save image hook here
        for key, image in kwargs.items():
            self.logger.send_image(key=os.path.join(self.prefix or "", namespace, key, "{:04d}.png".format(step)),
                                   data=image)

    def log_pyplot(self, step, fig, namespace="figures", key=None):
        if self.step != step and self.step is not None:
            self.flush()
        self.step = step
        self.timestamp = np.datetime64(datetime.now())
        image = self.plt2data(fig)
        self.logger.send_image(key=os.path.join(self.prefix or "", namespace, key or "{:04d}.png".format(step)),
                               data=image)

    @staticmethod
    def plt2data(fig):
        """
        @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
        @param fig a matplotlib figure
        @return a numpy 3D array of RGBA values
        """
        # draw the renderer
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

    def print(self, *args, sep=' ', end='\n', silent=False, **kwargs):
        text = sep.join(args) + end
        if not silent:
            print(*args, sep=sep, end=end)
        self.log_text(text, silent=True)

    def log_text(self, text, filename="text.log", silent=False):
        # todo: consider adding step to this
        if not silent:
            print(text)
        self.logger.log_text(key=os.path.join(self.prefix or "", filename), text=text)


logger = ML_Logger()
