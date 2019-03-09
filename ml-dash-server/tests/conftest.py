TEST_LOG_DIR = '../../runs'


def pytest_addoption(parser):
    parser.addoption('--log-dir',
                     action='store',
                     default=TEST_LOG_DIR,
                     help="The logging path for the test.")
