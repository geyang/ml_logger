from random import randint


def factory(module, name):
    class Lie:
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

    return Lie


import pickle


class Whatever(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except:
            return factory(module, name)


def load_from_pickle(path='parameters.pkl'):
    with open(path, 'rb') as f:
        yield from load_from_pickle_file(f)


def load_from_pickle_file(file):
    while True:
        try:
            yield Whatever(file).load()
        except EOFError:
            break


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
