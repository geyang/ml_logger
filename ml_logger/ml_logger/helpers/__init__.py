from random import randint

import pickle


class Whatever(pickle.Unpickler):
    def __init__(self, *_, **__):
        super().__init__(*_, **__)

    @staticmethod
    def cls_factory(module, name):

        class Unavailable:
            __dict__ = {}

            def __init__(self, *args, **kwargs):
                print(args, kwargs)
                self.__d = dict()

            def __setitem__(self, key, value):
                self.__d[key] = value

            def __getitem__(self, item):
                return self.__d[item]

            def __call__(self, *args, **kwargs):
                print(args, kwargs)

            def __repr__(self):
                return f"<class '{module}.{name}'>"

        return Unavailable

    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except:
            return self.cls_factory(module, name)


def load_from_pickle(path='parameters.pkl', **__):
    with open(path, 'rb') as f:
        yield from load_from_pickle_file(f, **__)


def load_from_pickle_file(file, **__):
    while True:
        try:
            yield Whatever(file, **__).load()
        except EOFError:
            break


def regularize_for_json(obj):
    from typing import Sequence
    from types import FunctionType
    import numpy as np
    if isinstance(obj, dict):
        return {k: regularize_for_json(v) for k, v in obj.items()}
    # elif isinstance(obj, tuple):
    #     return (regularize_for_json(i) for i in obj)
    # elif isinstance(obj, list):
    #     return [regularize_for_json(i) for i in obj]
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, float):
        return obj
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, np.ndarray) or isinstance(obj, np.ma.MaskedArray):
        return obj.tolist()
    elif isinstance(obj, Sequence):
        return [regularize_for_json(i) for i in obj]
    elif isinstance(obj, FunctionType):
        # todo: use $type syntax:
        #   $type: lambda
        #   $type: function
        return repr(obj)
    try:
        # todo: use $type syntax: $type: class
        return {k: regularize_for_json(v) for k, v in vars(obj).items()}
    except:
        return repr(obj)


def load_from_file(path):
    with open(path, 'rb') as f:
        while True:
            blob = f.read()
            if blob == b'':
                break
            yield blob


def sample(stream, k):
    """

    :param stream:
    :param k: the reservoir size
    :return:
    """

    reservoir = []
    for count, d in enumerate(stream):
        if count < k:
            reservoir.append((count, d))
        else:
            ind = randint(0, count)
            if ind < k:
                reservoir[ind] = (count, d)
    for i, d in sorted(reservoir, key=lambda t: t[0]):
        yield d


def load_pickle_as_dataframe(path='data.pkl', k=None):
    import pandas
    if k:
        d = pandas.DataFrame([_ for _ in sample(load_from_pickle(path), k)])
    else:
        d = pandas.DataFrame([_ for _ in load_from_pickle(path)])
    return d


if __name__ == "__main__":
    sampled = sample(range(100), 1)
    print(list(sampled))
    sampled = sample(range(100), 2)
    print(list(sampled))
    sampled = sample(range(100), 3)
    print(list(sampled))
    sampled = sample(range(100), 30)
    print(list(sampled))
