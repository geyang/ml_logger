import pytest

from ml_logger import logger


@pytest.fixture(scope='session')
def log_dir(request):
    return request.config.getoption('--logdir')


@pytest.fixture(scope="session")
def setup(log_dir):
    logger.configure('main_test_script', root=log_dir)
    logger.remove('')


class SomeClass:
    name = "local class"


def some_func():
    return 5


def test_pkl_lambda(setup):
    config = dict(lmb_fn=lambda x: x * 2,
                  some_fn=some_func,
                  local_cls=SomeClass,
                  local_obj=SomeClass())
    logger.remove('test_data.pkl')

    with logger.Sync():
        logger.save_pkl(config, "test_data.pkl", use_dill=True)

    loaded_config, = logger.load_pkl("test_data.pkl")
    assert loaded_config['lmb_fn'](2) == 4
    assert loaded_config['some_fn']() is 5


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
