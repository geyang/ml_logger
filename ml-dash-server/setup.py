from os import path
from setuptools import setup, find_packages

cwd = path.dirname(__file__)
with open(path.join(cwd, 'README'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(cwd, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(name="ml-dash",
      description="A Beautiful Visualization Dashboard For Machine Learning",
      long_description=long_description,
      version=version,
      url="https://github.com/episodeyang/ml_logger/tree/master/ml-dash-server",
      author="Ge Yang",
      author_email="yangge1987@gmail.com",
      license=None,
      keywords=["ml_logger",
                "ml-logger",
                "ml dash",
                "ml-dash",
                "ml_dash"
                "dashboard",
                "machine learning",
                "vis_server",
                "logging",
                "debug",
                "debugging"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "Programming Language :: Python :: 3"
      ],
      packages=[p for p in find_packages() if p != "tests"],
      include_package_data=True,
      install_requires=[
          "cloudpickle",
          'dill',
          'graphene',
          "graphql-core",
          "graphql-relay",
          'hachiko',
          "numpy",
          'pandas',
          "params_proto",
          "requests",
          "requests_futures",
          'ruamel.yaml',
          'sanic',
          'sanic-cors',
          'sanic-graphql',
          "termcolor",
          "typing"
      ])
