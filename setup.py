from os import path
from setuptools import setup

with open(path.join(path.abspath(path.dirname(__file__)), 'README'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(path.abspath(path.dirname(__file__)), 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(name="ml_logger",
      description="A print and debugging utility that makes your error printouts look nice",
      long_description=long_description,
      version=version,
      url="https://github.com/episodeyang/ml_logger",
      author="Ge Yang",
      author_email="yangge1987@gmail.com",
      license=None,
      keywords=["ml_logger", "logging", "debug", "debugging"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "Programming Language :: Python :: 3"
      ],
      packages=["ml_logger"],
      install_requires=["typing", "numpy", "params_proto", "cloudpickle", "japronto", "uvloop==0.8.1", "requests"]
      )
