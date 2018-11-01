from os import path
from setuptools import setup

with open(path.join(path.abspath(path.dirname(__file__)), 'README'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(path.abspath(path.dirname(__file__)), 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(name="ml-dash",
      description="A Beautiful Visualization Dashboard For Machine Learning",
      long_description=long_description,
      version=version,
      url="https://github.com/episodeyang/ml_dash",
      author="Ge Yang",
      author_email="yangge1987@gmail.com",
      license=None,
      keywords=["ml_logger", "ml_dash", "ml-dash", "ml dash", "dashboard", "machine learning", "vis_server" "logging",
                "debug", "debugging"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "Programming Language :: Python :: 3"
      ],
      packages=["ml_dash"],
      install_requires=["typing", "numpy", "termcolor", "params_proto", "cloudpickle",
                        "uvloop==0.8.1", "requests", "requests_futures", 'hachiko', 'sanic',
                        'sanic-cors', 'dill', 'ruamel.yaml']
      )
