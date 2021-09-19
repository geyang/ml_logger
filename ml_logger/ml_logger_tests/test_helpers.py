import os


class SomeClass:
    name = "local class"


def some_func():
    pass


def test_pkl_lambda():
    from ml_logger import logger

    config = dict(lmb_fn=lambda x: x * 2,
                  some_fn=some_func,
                  local_cls=SomeClass,
                  local_obj=SomeClass())
    logger.remove('test_data.pkl')
    logger.save_pkl(config, "test_data.pkl", use_dill=True)


def test_read_lambda():
    """veryfy that the object is correct"""
    from ml_logger import logger
    data, = logger.load_pkl("./test_data.pkl")
    print(*[f"{k}: {type(v)} - {str(v)}" for k, v in data.items()], sep="\n")
    # verify type of values


def xtest_json():
    """This should result in strings for most of the items"""
    from ml_dash.schema.files.file_helpers import read_pickle_for_json
    data, = read_pickle_for_json("./test_data.pkl")

    print(data)
    print(*[f"{k}: {str(v)}" for k, v in data.items()], sep="\n")
    import json
    serialized = json.dumps(data, separators=(",", ":"))
    print(serialized)


def test_cleanup():
    from ml_logger import logger

    logger.remove("test_data.pkl")
