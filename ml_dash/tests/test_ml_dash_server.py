"""
Tests for the ml-dash server.
"""
import pytest
from time import sleep
from os.path import join as pathJoin
from tests.conftest import LOCAL_TEST_DIR


@pytest.fixture(scope='session')
def log_dir(request):
    return request.config.getoption('--log-dir')


@pytest.fixture(scope="session")
def setup(log_dir):
    print('setup is complete!')


def test_default(setup):
    pass


if __name__ == "__main__":
    setup(LOCAL_TEST_DIR)
    test_default(None)
