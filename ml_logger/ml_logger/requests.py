from json import dumps, loads


class Result:
    def __init__(self, response):
        self.response = response

    def json(self):
        return loads(self.text)

    @property
    def text(self):
        return self.response.data.decode('utf8')

    def ok(self):
        return self.response.ok


class Response:
    def __init__(self, response):
        self.response = response

    def result(self):
        return self.response


class SyncRequests:
    def __init__(self, **kwargs):
        """
        To set the proxy:

        if proxy:
            # conditionally detect proxy setting
            if proxy.startswith("https://"):
                self.session.proxies = {"https": proxy[8:]}
            elif proxy.startswith("http://"):
                self.session.proxies = {"http": proxy[7:]}
            else:
                self.session.proxies = {"http": proxy}

        :param max_workers:
        :param proxy: only one proxy is supported with urllib3.
        """
        from requests import Session

        self.session = Session(**kwargs)

    def get(self, *args, **kwargs):
        _ = self.session.get(*args, **kwargs)
        return Response(_)

    def put(self, *args, **kwargs):
        _ = self.session.put(*args, **kwargs)
        return Response(_)

    def post(self, *args, **kwargs):
        _ = self.session.post(*args, **kwargs)
        return Response(_)

    def delete(self, *args, **kwargs):
        _ = self.session.delete(*args, **kwargs)
        return Response(_)

    def fetch(self, *args, **kwargs):
        _ = self.session.fetch(*args, **kwargs)
        return Response(_)


class xResponse:
    def __init__(self, response):
        self.response = response

    def result(self):
        return Result(self.response)


class xSyncRequests:
    def __init__(self, max_workers=1, proxy=None, **kwargs):
        """
        :param max_workers:
        :param proxy: only one proxy is supported with urllib3.
        """
        import urllib3
        retries = urllib3.Retry(connect=5, read=2, redirect=5)
        if proxy:
            self.pool = urllib3.ProxyManager(proxy_url=proxy, num_pools=max_workers, retries=retries, **kwargs)
        else:
            self.pool = urllib3.PoolManager(num_pools=max_workers, retries=retries, **kwargs)

    def get(self, *args, json, **kwargs):
        _ = self.pool.request('GET', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return xResponse(_)

    def put(self, *args, json, **kwargs):
        _ = self.pool.request('PUT', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return xResponse(_)

    def post(self, *args, json=None, data=None, **kwargs):
        if json is None:
            _ = self.pool.request('POST', *args, body=data, **kwargs)
        else:
            _ = self.pool.request('POST', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return xResponse(_)

    def delete(self, *args, json, **kwargs):
        _ = self.pool.request('DELETE', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return xResponse(_)

    def fetch(self, *args, json, **kwargs):
        _ = self.pool.request('FETCH', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return xResponse(_)
