import os
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from ml_logger.serdes import serialize, deserialize
from ml_logger.server import LoggingServer
from ml_logger.struts import ALLOWED_TYPES, LogEntry, LogOptions, LoadEntry, RemoveEntry, PingData


class LogClient:
    local_server = None
    session = None

    def __init__(self, url: str = None, max_workers=None):
        if url.startswith("file://"):
            self.local_server = LoggingServer(data_dir=url[6:], silent=True)
        elif os.path.isabs(url):
            self.local_server = LoggingServer(data_dir=url, silent=True)
        elif url.startswith('http://'):
            self.url = url
            self.ping_url = os.path.join(url, "ping")
            self.session = FuturesSession(ThreadPoolExecutor(max_workers=max_workers) if max_workers else None)
        else:
            # todo: add https://, and s3://
            raise TypeError('log url need to begin with `/`, `file://` or `http://`.')

    configure = __init__

    def _get(self, key, dtype):
        if self.local_server:
            return self.local_server.load(key, dtype)
        else:
            json = LoadEntry(key, dtype)._asdict()
            # note: reading stuff from the server is always synchronous via the result call.
            res = self.session.get(self.url, json=json).result()
            result = deserialize(res.text)
            return result

    def _post(self, key, data, dtype, options: LogOptions = None):
        if self.local_server:
            self.local_server.log(key, data, dtype, options)
        else:
            # todo: make the json serialization more robust. Not priority b/c this' client-side.
            json = LogEntry(key, serialize(data), dtype, options)._asdict()
            self.session.post(self.url, json=json)

    def _delete(self, key):
        if self.local_server:
            self.local_server.remove(key)
        else:
            # todo: make the json serialization more robust. Not priority b/c this' client-side.
            json = RemoveEntry(key)._asdict()
            self.session.delete(self.url, json=json)

    def ping(self, exp_key, status, _duplex=True, burn=True):
        # todo: add configuration for early termination
        if self.local_server:
            signals = self.local_server.ping(exp_key, status)
            return deserialize(signals) if _duplex else None
        else:
            # todo: make the json serialization more robust. Not priority b/c this' client-side.
            ping_data = PingData(exp_key, status, burn=burn)._asdict()
            req = self.session.post(self.ping_url, json=ping_data)
            if _duplex:
                response = req.result()
                # note: I wonder if we should raise if the response is non-ok.
                return deserialize(response.text) if response.ok else None

    # send signals to the worker
    def send_signal(self, exp_key, signal=None):
        options = LogOptions(overwrite=True)
        channel = os.path.join(exp_key, "__signal.pkl")
        self._post(channel, signal, dtype="log", options=options)

    # Reads binary data
    def read(self, key):
        return self._get(key, dtype="read")

    # Reads binary data
    def read_pkl(self, key):
        return self._get(key, dtype="read_pkl")

    def read_np(self, key):
        return self._get(key, dtype="read_np")

    # appends data
    def log(self, key, data, **options):
        self._post(key, data, dtype="log", options=LogOptions(**options))

    # appends text
    def log_text(self, key, text):
        self._post(key, text, dtype="text")

    # sends out images
    def send_image(self, key, data):
        assert data.dtype in ALLOWED_TYPES, "image data must be one of {}".format(ALLOWED_TYPES)
        self._post(key, data, dtype="image")

    # appends text
    def log_buffer(self, key, buf):
        self._post(key, buf, dtype="byte")
