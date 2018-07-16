from random import randint


def load_from_pickle(path='parameters.pkl'):
    import dill
    with open(path, 'rb') as f:
        while True:
            try:
                yield dill.load(f)
            except EOFError:
                break


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
