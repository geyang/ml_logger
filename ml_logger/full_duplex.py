import threading
import time

from . import LogClient


class Duplex(object):
    """ Duplex Agent
    The full duplex agent runs in the background. This is responsible for maintaining `alive` (running) state
    when the main thread is running. This also allows duplex communication (lots of delay though) with the
    server without using `server-sent-events` or `websocket`.

    When you call

    ```
    command, = logger.ping(message="running")
    # or
    commands = logger.ping(message="running", no_intercept=False)
    ```

    You can in fact get return commands. If the return command if "stop", the ping function raises an exception, and
    stops the training.
    """

    def __init__(self, log_client: LogClient, prefix, keep_alive_interval=10, ):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.prefix = prefix
        self.log_client = log_client
        self.keep_alive_interval = keep_alive_interval

        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True  # Daemonize thread

    def start(self):
        self.thread.start()

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            time.sleep(self.keep_alive_interval)

    def send_alive(self):
        raise NotImplemented
