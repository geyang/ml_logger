def pytest_addoption(parser):
    parser.addoption('--log-dir', action='store', default='/tmp/ml-logger-debug',
                     help="The logging path for the test.")
