"""
# Tests for ml-logger.
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
    assert local_prefix + '/test_cloud.py' in glob.glob(local_prefix + "/*")
    logger.remove("test_dir_download")


def test_gs_upload(setup):
    import os, pathlib

    gs_bucket = os.environ['ML_LOGGER_TEST_GS_BUCKET']

    target = "gs://" + gs_bucket + "/test_dir.tar"
    logger.upload_dir(pathlib.Path(__file__).absolute().parent, target)


def test_gs_download(setup):
    import os, glob

    gs_bucket = os.environ['ML_LOGGER_TEST_GS_BUCKET']

    source = "gs://" + gs_bucket + "/test_dir.tar"
    local_prefix = '/tmp/test_dir_download'
    logger.download_dir(source, to=local_prefix)
    assert local_prefix + '/test_cloud.py' in glob.glob(local_prefix + "/*")
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


def test_gs_glob(setup):
    import os

    gs_bucket = os.environ.get('ML_LOGGER_TEST_GS_BUCKET', None)

    target = "gs://" + gs_bucket + "/test_dir.tar"
    logger.upload_dir('.', target)

    files = logger.glob_gs(gs_bucket)
    assert 'test_dir.tar' in files

    files = logger.glob_gs(wd=gs_bucket)
    assert 'test_dir.tar' in files

    files = logger.glob_gs(gs_bucket + "/test_dir.tar")
    assert 'test_dir.tar' in files

    files = logger.glob_gs(gs_bucket + "/this_does_not_exist")
    assert not files


def test_gs_glob_prefix(setup):
    import os

    gs_bucket = os.environ.get('ML_LOGGER_TEST_GS_BUCKET', None)

    target = "gs://" + gs_bucket + "/prefix/prefix-2/test_dir.tar"
    logger.upload_dir(".", target)
    files = logger.glob_gs(wd=gs_bucket + "/prefix/prefix-2")
    assert 'test_dir.tar' in files
