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
    import os

    s3_bucket = os.environ['ML_LOGGER_TEST_S3_BUCKET']

    target = "s3://" + s3_bucket + "/test_dir.tar"
    print('uploading to', target)
    logger.upload_dir(".", target)
    print("uploaded to", target)


def test_s3_download(setup):
    from pathlib import Path
    import os, shutil

    s3_bucket = os.environ['ML_LOGGER_TEST_S3_BUCKET']

    source = "s3://" + s3_bucket + "/test_dir.tar"
    to_local = Path(logger.root) / logger.prefix / 'test_dir_download'
    logger.download_dir(source, to=to_local)

    assert to_local.exists()
    print('should replicate this code folder')
    assert (to_local / 'test_dir_upload.py').exists()
    shutil.rmtree(to_local)


def test_gs_upload(setup):
    import os

    gs_bucket = os.environ['ML_LOGGER_TEST_GS_BUCKET']

    target = "gs://" + gs_bucket + "/test_dir.tar"
    print('uploading to', target)
    logger.upload_dir(".", target)
    print("uploaded to", target)


def test_gs_download(setup):
    from pathlib import Path
    import os, shutil

    gs_bucket = os.environ['ML_LOGGER_TEST_GS_BUCKET']

    source = "gs://" + gs_bucket + "/test_dir.tar"
    to_local = Path(logger.root) / logger.prefix / 'test_dir_download'
    logger.download_dir(source, to=to_local)

    assert to_local.exists()
    print('should replicate this code folder')
    assert (to_local / 'test_dir_upload.py').exists()
    shutil.rmtree(to_local)


def test_s3_glob(setup):
    import os

    s3_bucket = os.environ['ML_LOGGER_TEST_S3_BUCKET']

    target = "s3://" + s3_bucket + "/test_dir.tar"
    logger.upload_dir(".", target)
    files = logger.glob_s3(s3_bucket)
    assert 'test_dir.tar' in files
