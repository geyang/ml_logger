.. _contents::

Welcome to ML-Logger!
=====================================

|Downloads|

.. |Downloads| image:: http://pepy.tech/badge/ml-logger
   :target: http://pepy.tech/project/ml-logger


ML-Logger makes it easy to:

-  save data locally and remotely, as **binary**, in a transparent
   ``pickle`` file, with the same API and zero configuration.
-  write from 500+ worker containers to a single instrumentation server
-  visualize ``matplotlib.pyplot`` figures from a remote server locally
   with ``logger.savefig('my_figure.png?raw=true')``

And ml-logger does all of these with *minimal configuration* — you can
use the same logging code-block both locally and remotely with no code-block change.

ML-logger is highly performant – the remote writes are asynchronous. For
this reason it doesn’t slow down your training even with 100+ metric
keys.

Why did we built this, you might ask? Because we want to make it easy
for people in ML to use the same logging code-block in all of they projects,
so that it is easy to get started with someone else’s baseline.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 3
   :glob:

   index
   installation
   usage
   modindex

