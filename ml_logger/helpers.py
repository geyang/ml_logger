def load_from_pickle(path='parameters.pkl'):
    import dill
    with open(path, 'rb') as f:
        while True:
            try:
                yield dill.load(f)
            except EOFError:
                break


def load_pickle_as_dataframe(path='data.pkl'):
    import pandas
    d = pandas.DataFrame([_ for _ in load_from_pickle(path)])
    return d
