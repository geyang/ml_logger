============
Installation
============

Install the package with pip

.. code-block:: bash

   pip install ml-logger

To make sure you use the newest version:

.. code-block:: bash

   pip install ml-logger --upgrade --no-cache

Now you can fire up an `ipython` console and start logging!

.. code-block:: python

   from ml_logger import logger
   # ~> logging data to /tmp/ml-logger-debug
   logger.configure('/tmp/ml-logger-debug')

   logger.log(metrics={'some_val/smooth': 10, 'status': f"step ({i})"}, reward=20, timestep=i)
   # flush the data, otherwise the value would be overwritten with new values in the next iteration.
   logger.flush()

outputs ~>

.. code-block:: text

   ╒════════════════════╤════════════════════════════╕
   │       reward       │             20             │
   ├────────────────────┼────────────────────────────┤
   │      timestep      │             0              │
   ├────────────────────┼────────────────────────────┤
   │  some val/smooth   │             10             │
   ├────────────────────┼────────────────────────────┤
   │       status       │          step (0)          │
   ├────────────────────┼────────────────────────────┤
   │      timestamp     │'2018-11-04T11:37:03.324824'│
   ╘════════════════════╧════════════════════════════╛

