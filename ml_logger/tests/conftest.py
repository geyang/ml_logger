LOCAL_TEST_DIR = '/tmp/ml-logger-debug'


def pytest_addoption(parser):
    parser.addoption('--log-dir', action='store', default=LOCAL_TEST_DIR,
                     help="The logging path for the test.")
