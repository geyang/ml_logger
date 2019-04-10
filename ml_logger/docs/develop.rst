To Develop
==========

First clone repo, install dev dependencies, and install the module under
evaluation mode.

.. code-block:: bash

   git clone https://github.com/episodeyang/ml_logger.git
   cd ml_logger && cd ml_logger && pip install -r requirements-dev.txt
   pip install -e .

Testing local-mode (without a server)
-------------------------------------

You should be inside ml_logger/ml_logger folder

.. code-block:: bash

   pwd # ~> ml_logger/ml_logger
   make test

Testing with a server (You need to do both for an PR)
-----------------------------------------------------

To test with a live server, first run (in a separate console)

.. code-block:: bash

   python -m ml_logger.server --log-dir /tmp/ml-logger-debug

or do:

.. code-block:: bash

   make start-test-server

Then run this test script with the option:

.. code-block:: bash

   python -m pytest tests --capture=no --log-dir http://0.0.0.0:8081

or do

.. code-block:: bash

   make test-with-server

Your PR should have both of these two tests working. ToDo: add CI to
this repo.

To Publish
~~~~~~~~~~

You need ``twine``, ``rst-lint`` etc, which are included in the
``requirements-dev.txt`` file.

