import os

TEST_LOG_DIR = os.path.expanduser('~/ml-logger-debug/runs')

def pytest_addoption(parser):
    parser.addoption('--log-dir',
                     action='store',
                     default=TEST_LOG_DIR,
                     help="The logging path for the test.")
