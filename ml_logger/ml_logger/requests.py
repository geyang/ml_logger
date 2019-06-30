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
        return Result(self.response)


class SyncRequests:
    def __init__(self, max_workers=1):
        import urllib3
        retries = urllib3.Retry(connect=5, read=2, redirect=5)
        self.pool = urllib3.PoolManager(num_pools=max_workers, retries=retries)

    def get(self, *args, json, **kwargs):
        _ = self.pool.request('GET', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return Response(_)

    def put(self, *args, json, **kwargs):
        _ = self.pool.request('PUT', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return Response(_)

    def post(self, *args, json, **kwargs):
        _ = self.pool.request('POST', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return Response(_)

    def delete(self, *args, json, **kwargs):
        _ = self.pool.request('DELETE', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return Response(_)

    def fetch(self, *args, json, **kwargs):
        _ = self.pool.request('FETCH', *args, body=dumps(json).encode('utf-8'), **kwargs)
        return Response(_)


class AsyncRequests:
    def __init__(self, max_workers=10):
        import urllib3
        self.pool = urllib3.PoolManager(num_pools=max_workers)
