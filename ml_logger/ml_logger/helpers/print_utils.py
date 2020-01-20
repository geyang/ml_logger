from collections.abc import Sequence
from itertools import zip_longest
import numpy as np

DEFAULT_FORMATS = {
    # refer to this issue: https://github.com/numpy/numpy/issues/5543 numpy has built-in stringify helper.
    "numpy": lambda v: np.array2string(v, precision=3, separator=',', suppress_small=True),
    float: lambda v: v.__format__(".3f"),
    int: str,
}


def _is_sequence(d):
    return isinstance(d, Sequence) or type(d) is np.ndarray and len(d.shape) > 0


class PrintHelper:
    def __init__(self, formatters: dict = None):
        self.formatters = DEFAULT_FORMATS.copy()
        if formatters is not None:
            self.formatters.update(formatters)

    def to_string(self, v):
        _t = type(v)
        if _t.__module__ in self.formatters:
            return self.formatters[_t.__module__](v)
        elif _t in self.formatters:
            return self.formatters[_t](v)
        else:
            return str(v)

    def format_tabular(self, data, do_not_print_list=tuple(), min_key_width=20, min_value_width=20):
        keys = [k for k in data.keys() if k not in do_not_print_list]
        if len(keys) > 0:
            max_key_len = max([min_key_width] + [len(k) for k in keys])
            max_value_len = max([min_value_width] + [len(self.to_string(data[k])) for k in keys])
            output = None
            for k in keys:
                v = self.to_string(data[k])
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

    def format_row_table(self, data, max_rows=None, do_not_print_list=tuple(), min_column_width=5):
        """applies to metrics keys with multiple values"""
        output = ""

        keys = [k for k in data.keys() if k not in do_not_print_list]
        values = [data[k][:max_rows] if _is_sequence(data[k]) else [data[k]] for k in keys]
        max_width = [max([min_column_width, len(k)] + [len(self.to_string(v)) for v in d]) for k, d in zip(keys, values)]
        output += '|'.join([f"{key.replace('-', ' '):^{w}}" for key, w in zip(keys, max_width)]) + "\n"
        output += "┿".join(["━" * w for w in max_width]) + "\n"
        for row in zip_longest(*values):
            output += '|'.join([f"{self.to_string(value):^{width}}" for value, width in zip(row, max_width)]) + "\n"
        return output


if __name__ == "__main__":
    import numpy as np
    from datetime import datetime

    data = dict(some=10, key=100, text="hey", array=np.random.rand(3),
                __timestamp=np.datetime64(datetime.now()))
    p = PrintHelper()
    s = p.format_tabular(data)
    print(s)

    data = dict(some=[10], key=[100], text=["short", "hey this is very long"], array=np.random.rand(2, 3))
    p = PrintHelper()
    s = p.format_row_table(data)
    print(s)
