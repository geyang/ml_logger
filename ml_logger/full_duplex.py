import threading
import time

from . import LogClient


class Duplex(object):
    """ Duplex Agent
    The full duplex agent should be started in the background.

    keey alive
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
