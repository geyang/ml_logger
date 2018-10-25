import threading
import time



class Duplex(object):
    """ Duplex Agent
    The full duplex agent runs in the background. This is responsible for maintaining `alive` (running) state
    when the main thread is running. This also allows duplex communication (lots of delay though) with the
    server without using `server-sent-events` or `websocket`.

    This is not necessary if we use websocket or other duplex communication protocols.

    When you call

    ```
    command, = logger.ping(message="running")
    # or
    commands = logger.ping(message="running", no_intercept=False)
    ```

    You can in fact get return commands. If the return command if "stop", the ping function raises an exception, and
    stops the training.

    ### Note

    Make this as thin as possible. 
    """

    def __init__(self, thunk, keep_alive_interval=10):
        """
        runs the thunk per interval. Saves the output of the
        thunk in the signal buffer.

        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.keep_alive_interval = keep_alive_interval
        self.thunk = thunk
        self.buffer = []
        self.send_buffer = []

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True  # Daemonize thread

    def start(self):
        self.thread.start()

    def run(self):
        """ Method that runs forever """
        import random  # add random bits to avoid simultaneous requests
        while True:
            try:
                r = self.thunk(*self.send_buffer)
                self.send_buffer.clear()
                if r is not None:
                    self.buffer.append(r)
                scale = 1 + (random.random() - 0.5) * 0.1
                time.sleep(self.keep_alive_interval * scale)
            except Exception as e:
                print(e)

    def control_thunk(self, signal=None):
        stream = self.thunk(signal) or []
        if stream:
            self.buffer.extend(stream)  # assuming that the stream is also a list.
            # You add the advanced signal handling here,
            # for example changing keep_alive_interval,

    def send(self, status=None):
        self.send_buffer.append(status)

    def read_buffer(self, burn=True):
        """
        clears the buffer upon reading. This way the buffer won't fill up.
        
        :param burn:
        :return:
        """
        _ = self.buffer.copy()
        if burn:
            self.buffer.clear()
        return _
