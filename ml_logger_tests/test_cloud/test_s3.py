"""
# AWS S3 Tests
"""
from os.path import join as pathJoin

import pytest
from ml_logger import logger


@pytest.fixture(scope='session')
def log_dir(request):
    return request.config.getoption('--logdir')


@pytest.fixture(scope="session")
def setup(log_dir):
    logger.configure('main_test_script', root=log_dir)
    print(f"logging to {pathJoin(logger.root, logger.prefix)}")


def test_s3_upload(setup):
    import os, pathlib

    profile = os.environ.get('ML_LOGGER_TEST_AWS_PROFILE', None)
    if profile:
        os.environ['AWS_PROFILE'] = profile

    s3_bucket = os.environ['ML_LOGGER_TEST_S3_BUCKET']

    target = "s3://" + s3_bucket + "/test_dir.tar"
    logger.upload_dir(pathlib.Path(__file__).absolute().parent, target)


def test_s3_download(setup):
    import os, glob

    profile = os.environ.get('ML_LOGGER_TEST_AWS_PROFILE', None)
    if profile:
        os.environ['AWS_PROFILE'] = profile

    s3_bucket = os.environ['ML_LOGGER_TEST_S3_BUCKET']

    source = "s3://" + s3_bucket + "/test_dir.tar"
    local_prefix = '/tmp/test_dir_download'
    logger.download_dir(source, to=local_prefix)
    assert local_prefix + '/test_s3.py' in glob.glob(local_prefix + "/*")
    logger.remove("test_dir_download")


def test_s3_glob(setup):
    import os

    profile = os.environ.get('ML_LOGGER_TEST_AWS_PROFILE', None)
    if profile:
        os.environ['AWS_PROFILE'] = profile

    s3_bucket = os.environ['ML_LOGGER_TEST_S3_BUCKET']

    target = "s3://" + s3_bucket + "/test_dir.tar"
    logger.upload_dir('.', target)

    files = logger.glob_s3(s3_bucket)
    assert 'test_dir.tar' in files

    files = logger.glob_s3(wd=s3_bucket)
    assert 'test_dir.tar' in files

    files = logger.glob_s3(s3_bucket + "/test_dir.tar")
    assert 'test_dir.tar' in files

    files = logger.glob_s3(s3_bucket + "/this_does_not_exist")
    assert not files


def test_s3_glob_prefix(setup):
    import os

    profile = os.environ.get('ML_LOGGER_TEST_AWS_PROFILE', None)
    if profile:
        os.environ['AWS_PROFILE'] = profile

    s3_bucket = os.environ['ML_LOGGER_TEST_S3_BUCKET']

    target = "s3://" + s3_bucket + "/prefix/prefix-2/test_dir.tar"
    logger.upload_dir(".", target)
    files = logger.glob_s3(wd=s3_bucket + "/prefix/prefix-2")
    assert 'test_dir.tar' in files


def test_s3_remove(setup):
    import os

    example_data = {'a': 1, 'b': 2}

    s3_bucket = os.environ.get('ML_LOGGER_TEST_S3_BUCKET', None)
    target = "s3://" + s3_bucket + "/prefix/prefix-2/example_data.pt"

    logger.save_torch(example_data, target)
    file, = logger.glob_s3(target[5:])
    logger.remove_s3(s3_bucket, file)
    assert not logger.glob_s3(target[5:])


def test_s3_upload_download_torch(setup):
    import os

    example_data = {'a': 1, 'b': 2}

    s3_bucket = os.environ.get('ML_LOGGER_TEST_S3_BUCKET', None)
    file = "prefix/prefix-2/example_data.pt"
    target = "s3://" + s3_bucket + "/" + file

    logger.remove_s3(s3_bucket, file)

    logger.save_torch(example_data, target)
    downloaded_data = logger.load_torch(target)
    assert downloaded_data['a'] == 1
    assert downloaded_data['b'] == 2
