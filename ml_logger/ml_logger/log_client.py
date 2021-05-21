import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from io import BytesIO, StringIO

from ml_logger.requests import SyncRequests
from ml_logger.serdes import serialize, deserialize
from ml_logger.server import LoggingServer
from ml_logger.struts import ALLOWED_TYPES, LogEntry, LogOptions, LoadEntry, RemoveEntry, PingData, GlobEntry
from requests_futures.sessions import FuturesSession


# noinspection PyPep8Naming
@contextmanager
def _SyncContext(logger, clean=False, max_workers=None):
    """
    Context function for Synchronous network sessions

    :param logger: logger object
    :param clean: remove sync_pool after __exit__()
    :param max_workers: urllib3 max_workers field
    :return:
    """
    old_session = logger.session
    if isinstance(old_session, SyncRequests):
        logger.sync_pool = old_session
    if logger.sync_pool:
        logger.session = logger.sync_pool
    else:
        logger.set_session(False, max_workers or logger.max_workers)
        if not clean:
            logger.sync_pool = logger.session
    try:
        yield
    finally:
        logger.session = old_session


class LogClient:
    local_server: LoggingServer = None
    session = None
    max_workers = None
    # note: used by the context switchers. They do not take parameters, so
    #  only sync/async key is needed to differentiate
    sync_pool = None
    async_pool = None

    def __init__(self, root: str = None, user=None, access_token=None, asynchronous=None, max_workers=None):
        """
        When max_workers is 0, the HTTP requests are synchronous. This allows one to make
        synchronous requests procedurally.

        This is also useful when some logging have to happen before forking subprocesses.
        Mujoco-py for example, would have trouble with forked processes if multiple
        threads are started before forking the subprocesses.

        :param root:
        :param asynchronous: If this is not None, we create a request pool. This way
            we can use the (A)SyncContext call right after construction.
        :param max_workers:
        """
        if asynchronous is not None:
            self.set_session(asynchronous, max_workers)

        if root.startswith("file://"):
            self.local_server = LoggingServer(cwd=root[6:], silent=True)
        elif os.path.isabs(root):
            self.local_server = LoggingServer(cwd=root, silent=True)
        elif root.startswith('http://'):
            self.local_server = None  # remove local server to use sessions.
            self.url = root
            self.access_token = access_token
            self.stream_url = os.path.join(root, "stream")
            self.ping_url = os.path.join(root, "ping")
            self.glob_url = os.path.join(root, "glob")
            # when setting sessions the first time, default to use Asynchronous Session.
            if self.session is None:
                asynchronous = True if asynchronous is None else asynchronous
                self.set_session(asynchronous, max_workers)
        else:
            # todo: add https://, and s3://
            raise TypeError('log url need to begin with `/`, `file://` or `http://`.')

    configure = __init__

    def set_session(self, asynchronous, max_workers, proxy=None):
        """
        
        :param asynchronous: bool
        :param max_workers: int for number of workers
        :return: 
        """
        if proxy is None:
            import os
            proxy = os.environ.get('http_proxy', None) or os.environ.get('HTTP_PROXY', None)

        self.max_workers = 10 if max_workers is None else max_workers

        if asynchronous is True:
            self.session = FuturesSession(ThreadPoolExecutor(max_workers=self.max_workers))
        elif asynchronous is False:
            self.session = SyncRequests()

    # noinspection PyPep8Naming
    def SyncContext(self, **kwargs):
        """
        Returns a context object in which the logger logs synchronously.

        :param clean: remove sync_pool after __exit__()
        :param max_workers: urllib3 max_workers field
        :return: context object
        """
        return _SyncContext(self, **kwargs)

    # noinspection PyPep8Naming
    def AsyncContext(self, **kwargs):
        """
        Returns a context object in which the logger logs asynchronously.

        :param clean: remove sync_pool after __exit__()
        :param max_workers: future_request.Session max_workers field
        :return: context object
        """
        return _AsyncContext(self, **kwargs)

    def _get(self, key, dtype, **options):
        if self.local_server:
            return self.local_server.load(key, dtype, **options)
        else:
            json = LoadEntry(key, dtype, **options)._asdict()
            # note: reading stuff from the server is always synchronous via the result call.
            res = self.session.get(self.url, json=json).result()
            # todo: better error handling.
            return deserialize(res.text)

    def _log(self, key, data, dtype, options: LogOptions = None):
        if self.local_server:
            self.local_server.log(key, data, dtype, options)
        else:
            # todo: make the json serialization more robust. Not priority b/c this' client-side.
            json = LogEntry(key, serialize(data), dtype, options)._asdict()
            self.session.post(self.url, json=json)

    def stream_download(self, path):
        buf = BytesIO()
        if self.local_server:
            for d in self.local_server.load(path, dtype="byte"):
                buf.write(d)
            buf.seek(0)
            return buf
        else:
            from requests_toolbelt.downloadutils import stream

            json = LoadEntry(path, "byte")._asdict()
            # note: reading stuff from the server is always synchronous.
            #  with (future) sessions, this is forced by the result call.
            r = self.session.get(self.stream_url, json=json, stream=True)
            assert stream.stream_response_to_file(r.result(), path=buf) is None
            buf.seek(0)
            return buf

    def save_buffer(self, buffer, key):
        # proxy = os.environ.get('HTTP_PROXY')
        # c.setopt(c.PROXY, proxy)
        # logger.print('proxy:', proxy)
        if isinstance(buffer, BytesIO):
            from requests_toolbelt import MultipartEncoder
            encoder = MultipartEncoder({'file': (key, buf), 'canary': true})
            self.session.post(self.url, data=encoder, headers={'Content-Type': encoder.content_type})
        elif isinstance(buffer, StringIO):
            from pycurl import Curl
            c = Curl()
            c.setopt(c.URL, self.url)
            c.setopt(c.TIMEOUT, 3600)
            c.setopt(c.HTTPPOST, [
                ('file', (
                    c.FORM_BUFFER, source_path,
                    c.FORM_BUFFERPTR, buffer.read(),
                    c.FORM_CONTENTTYPE, 'plain/text',
                )),
            ])
            c.perform()
            c.close()

    def save_file(self, source_path, key):
        """

        :param source_path: is relative to the local file system.
        :param key: the key is relative to the current prefix.
        :return:
        """
        if self.local_server:
            if source_path.startswith('/'):
                source_path = "/" + source_path
            return self.local_server.copy(source_path, key)
        # proxy = os.environ.get('HTTP_PROXY')
        # c.setopt(c.PROXY, proxy)
        # logger.print('proxy:', proxy)
        from pycurl import Curl
        c = Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.TIMEOUT, 3600)
        c.setopt(c.HTTPPOST, [
            ('file', (
                c.FORM_FILE, source_path,
                c.FORM_FILENAME, key,
                c.FORM_CONTENTTYPE, 'plain/text',
            )),
        ])
        c.perform()
        c.close()

    def glob(self, query, **kwargs):
        if self.local_server:
            return self.local_server.glob(query, **kwargs)
        else:
            # todo: make the json serialization more robust. Not priority b/c this' client-side.
            json = GlobEntry(query, **kwargs)._asdict()
            res = self.session.post(self.glob_url, json=json).result()
            return res.json()

    def delete(self, key):
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
        self._log(channel, signal, dtype="log", options=options)

    # Reads binary data
    def read(self, key, start=None, stop=None):
        return self._get(key, dtype="byte", start=start, stop=stop)

    def read_text(self, key):
        return self._get(key, dtype="text")

    # Reads binary data
    def read_pkl(self, key, start=None, stop=None):
        return self._get(key, dtype="pkl", start=start, stop=stop)

    def read_np(self, key):
        return self._get(key, dtype="np")

    def read_json(self, key):
        return self._get(key, dtype="json")

    def read_h5(self, key):
        return self._get(key, dtype="h5")

    # read_buffer is an alias of read, which returns the buffer.
    read_buffer = read

    # appends data
    def log(self, key, data, **options):
        self._log(key, data, dtype="log", options=LogOptions(**options))

    # appends text
    def log_text(self, key, text, **options):
        self._log(key, text, dtype="text", options=LogOptions(**options))

    # appends yaml
    def log_yaml(self, key, data):
        # does not support appending yet
        self._log(key, data, dtype="yaml")

    # sends out images
    def send_image(self, key, data):
        assert data.dtype in ALLOWED_TYPES, "image data must be one of {}".format(ALLOWED_TYPES)
        self._log(key, data, dtype="image", options=LogOptions(overwrite=True))

    # writes data
    def log_buffer(self, key, buf, **options):
        # defaults to overwrite for binary data.
        self._log(key, buf, dtype="byte", options=LogOptions(**options))
        # self._multipart(key, buf, options=LogOptions(**options))
