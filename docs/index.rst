.. _contents::

#################################
Introducing Ml-Logger
#################################

|Downloads|

.. |Downloads| image:: http://pepy.tech/badge/ml-logger
   :target: http://pepy.tech/project/ml-logger

- Does Tensorboard feel slow to you?
- Do you have trouble managing hundreds of runs, and 20 different experiments?
- Does the Protobuff that tensorboardX uses feel too opaque, and hard to read from for analysis?

**I do**. This is why I wrote ML-Logger and a ML-Dash, two open-source distributed logging and visualization library for you, and your University collaborators who want to work on the same code!

To get started: ml-logger uses :code:`pycurl` for fast file upload. The easiest way to install :code:`pycurl`, is to use conda. First run: :code:`conda install pycurl`. Then, install ml-logger using pip: :code:`pip install ml-logger`.

.. code:: bash

    conda install pycurl
    pip install ml-logger ml-dash pandas
    python -m ml_dash.app

Now you can start logging your experiments! Here is a simple example:

.. code:: python

    from ml_logger import logger
    import numpy as np

    logger.log_params(train={"learning_rate": 0.001})
    logger.job_started()

    print(logger)
    print(logger.get_dash_url())

    for i in range(20):
        logger.log(step=i, loss=np.random.random() * np.exp(- 0.2 * i))
        logger.flush()

    logger.job_completed()

::

    /Users/david/berkeley/packages/ml_logger/ml-dash-server/ml_dash/client-dist

        You can now view ml-dash client in the browser.

          Local: 'http://localhost:3001/

        To update to the newer version, do
        ~> pip install --upgrade ml-dash

    [2019-06-05 20:56:33 -0700] [46329] [INFO] Going Fast @ 'http://127.0.0.1:3001
    [2019-06-05 20:56:33 -0700] [46329] [INFO] Starting worker [46329]

ML-Logger
=========

- Saves all data in a folder structure (S3 and other backend coming soon)
- Built-in support Tensorflow + pyTorch
- Fast, extremely so
- Logging API that has standardized over 1 and half year of development
- battled hardened -- was handling 3000 rps on a single server
- Support saving in pickle and numpy formats

Log it, and read it later for Analysis!
========================================

supports two way communication between the job and the instrumentation server. Want to run some analysis on a model trained last week? No problem! just do

.. code:: python

    logger.load_module(<NNModule>, key="username/project/run-id/models/blah.pkl").

Fast and Furious
=================


Did I mention that ML-Logger is uber-fast? We make the IO requests asynchronously, so that you main code doesn't slow down. We also support local metrics cache, so that you only send the summary of the metrics :).

Oh, for logging videos, we first compress the frame tensor 200x. And we support live plotting with Matplotlib!


#################################
ML-Dash
#################################

A Visualization Dashboard designed from ground up, to replace Tensorboard and Visdom.

Pictures are worth a thousand words--see below!

RoadMap
--------

- Adding support for custom Viewers, so that you add custom views specific for your project, such as webGL rendered 3D mesh.


..

    .. toctree::
       :maxdepth: 0
       :glob:

       setting_up
       usage
       modindex
       develop
       develop_ml_dash

