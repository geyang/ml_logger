from os.path import join as pathJoin
from time import sleep

import pytest

from ml_logger import logger
from ml_logger.helpers.color_helpers import percent
from ml_logger.ml_logger import Color, metrify


@pytest.fixture(scope='session')
def log_dir(request):
    return request.config.getoption('--logdir')


@pytest.fixture(scope="session")
def setup(log_dir):
    logger.configure('main_test_script', root=log_dir)
    print('cleaning this directory')
    logger.remove('')
    print(f"logging to {pathJoin(logger.root, logger.prefix)}")


@pytest.fixture(scope="session")
def setup_no_clean(log_dir):
    logger.configure('main_test_script', root=log_dir)

    print(f"logging to {pathJoin(logger.root, logger.prefix)}")


def test_upload_dir(setup):
    import os, glob

    logger.upload_dir(".", "upload_dir/target.tar", excludes=["*.pyc", ".git"])
    files = logger.glob("**/*", wd="upload_dir")
    assert "target.tar" in files, "the upload should complete"
    logger.remove("upload_dir")


def test_upload_files(setup):
    import os, glob

    files = glob.glob("**/*.*", recursive=True)
    for file in files:
        logger.upload_file(file, "target/" + file)
        logger.glob("target/**/*")

    server_files = logger.glob("**/*.*", wd="target")
    assert len(server_files) == len(files), "the list should be the same."


def test_download_dir(setup_no_clean):
    import os, glob, shutil

    with logger.Sync():
        logger.make_archive("target", root_dir="target")

    logger.download_dir("target.tar", "/tmp/target")
    downloaded = glob.glob("/tmp/target/**/*.*", recursive=True)
    assert "/tmp/target/test_file_utils.py" in downloaded, "the file should exist"
    shutil.rmtree("/tmp/target")
    logger.remove("target", "target.tar")
