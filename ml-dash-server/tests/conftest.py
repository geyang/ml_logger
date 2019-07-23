from os.path import expanduser

TEST_LOG_DIR = expanduser('~/ml-logger-debug')


def pytest_addoption(parser):
    parser.addoption('--log-dir',
                     action='store',
                     default=TEST_LOG_DIR,
                     help="The logging path for the test.")
