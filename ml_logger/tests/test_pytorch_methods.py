"""
In this file we test the tensorflow specific logging methods.
"""
import pytest
from ml_logger import logger
from tests.test_ml_logger import setup, log_dir
from tests.conftest import LOCAL_TEST_DIR
import torch.nn as nn


class View(nn.Module):
    def __init__(self, *size):
        """
        reshape nn module.

        :param size: reshapes size of tensor to [batch, *size]
        """
        super().__init__()
        self.size = size

    def forward(self, x):
        return x.view(-1, *self.size)


demo_module = nn.Sequential(
    nn.Conv2d(20, 32, kernel_size=4, stride=2),
    nn.BatchNorm2d(32),
    nn.ReLU(),
    nn.Conv2d(32, 64, kernel_size=4, stride=2),
    nn.BatchNorm2d(64),
    nn.ReLU(),
    nn.Conv2d(64, 64, kernel_size=4, stride=2),
    nn.BatchNorm2d(64),
    nn.ReLU(),
    nn.Conv2d(64, 32, kernel_size=4, stride=2),
    nn.BatchNorm2d(32),
    nn.ReLU(),
    View(128),
    nn.Linear(128, 128),
    nn.ReLU(),
    nn.Linear(128, 100),
    nn.ReLU(),
    nn.Linear(100, 1)
)


def test_module(setup):
    logger.save_module(demo_module, "modules/test_module.pkl", show_progress=True)


def xtest_modules(setup):
    logger.save_modules(mod_0=demo_module, mod_1=demo_module, path="modules/test_modules.pkl")


def test_load_module(setup):
    test_module(setup)  # save the module weights first
    logger.load_module(demo_module, "modules/test_module.pkl")


if __name__ == "__main__":
    setup(LOCAL_TEST_DIR)
    test_module(setup)
    # test_modules(setup)
    test_load_module(setup)
