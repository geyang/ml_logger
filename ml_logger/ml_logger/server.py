import os
from datetime import datetime
import numpy as np
import dill  # done: switch to dill instead
from params_proto import cli_parse, Proto, BoolFlag
from ml_logger.serdes import deserialize, serialize
from ml_logger.struts import ALLOWED_TYPES, LogEntry, LogOptions, LoadEntry, RemoveEntry, PingData, GlobEntry


class LoggingServer:
    silent = None

    def __init__(self, data_dir, silent=False):
        assert os.path.isabs(data_dir)
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.silent = silent
        if not silent:
            print('logging data to {}'.format(data_dir))

    configure = __init__

    def serve(self, host, port, workers):
        import sanic
        self.app = sanic.Sanic()
        self.app.add_route(self.log_handler, '/', methods=['POST'])
        self.app.add_route(self.read_handler, '/', methods=['GET'])
        self.app.add_route(self.ping_handler, '/ping', methods=['POST'])
        self.app.add_route(self.glob_handler, '/glob', methods=['POST'])
        self.app.add_route(self.remove_handler, '/', methods=['DELETE'])
        # todo: need a file serving url
        self.app.run(host=host, port=port, workers=workers, debug=Params.debug)

    async def ping_handler(self, req):
        import sanic
        if not req.json:
            msg = f'request json is empty: {req.text}'
            print(msg)
            return sanic.response.text(msg)
        ping_data = PingData(**req.json)
        print("received ping data: {} type: {}".format(ping_data.status, ping_data.exp_key))
        data = self.ping(ping_data.exp_key, ping_data.status, ping_data.burn)
        return sanic.response.text(data)

    def ping(self, exp_key, status, burn=True):
        status_path = os.path.join(exp_key, '__presence')
        self.log(status_path, dict(status=status, time=datetime.now()), dtype="yaml",
                 options=LogOptions(overwrite=True, write_mode='key'))
        signal_path = os.path.join(exp_key, '__signal.pkl')
        res = self.load(signal_path, 'read_pkl')
        if burn:
            self.remove(signal_path)
        return serialize(res)

    async def glob_handler(self, req):
        import sanic
        if not req.json:
            msg = f'request json is empty: {req.text}'
            print(msg)
            return sanic.response.text(msg)

        glob_entry = GlobEntry(**req.json)
        print("globbing: work directory {} query: {} is_recursive: {} start: {}, stop: {}".format(
            glob_entry.wd, glob_entry.query, glob_entry.recursive, glob_entry.start, glob_entry.stop))
        try:
            file_paths = self.glob(query=glob_entry.query, wd=glob_entry.wd,
                                   recursive=glob_entry.recursive,
                                   start=glob_entry.start, stop=glob_entry.stop, )
            return sanic.response.json(file_paths, status=200)
        # note: do we need this? sanic doesn't already do this?
        except FileNotFoundError as e:
            return sanic.response.text(e, status=404)

    async def read_handler(self, req):
        import sanic
        if not req.json:
            msg = f'request json is empty: {req.text}'
            print(msg)
            return sanic.response.text(msg)
        load_entry = LoadEntry(**req.json)
        print("loading: {} type: {}: start: {}, stop: {}".format(
            load_entry.key, load_entry.type, load_entry.start, load_entry.stop))
        res = self.load(load_entry.key, load_entry.type, load_entry.start, load_entry.stop)
        data = serialize(res)
        return sanic.response.text(data)

    async def remove_handler(self, req):
        import sanic
        if not req.json:
            msg = f'request json is empty: {req.text}'
            print(msg)
            return sanic.response.text(msg)
        remove_entry = RemoveEntry(**req.json)
        print("removing: {}".format(remove_entry.key))
        self.remove(remove_entry.key)
        return sanic.response.text('ok')

    async def log_handler(self, req):
        import sanic
        if not req.json:
            print(f'request json is empty: {req.text}')
            return sanic.response.text("Reuqest json is empty")
        log_entry = LogEntry(**req.json)
        print("writing: {} type: {} options: {}".format(log_entry.key, log_entry.type, log_entry.options))
        data = deserialize(log_entry.data)
        options = log_entry.options if log_entry.options is None else LogOptions(*log_entry.options)
        self.log(log_entry.key, data, log_entry.type, options)
        return sanic.response.text('ok')

    def glob(self, query, wd, recursive, start, stop):
        """
        Glob under the work directory. (so that the wd is not included in the file paths that are returned.)

        :param query: we remove the leading slash so that //home/directory allows you to access absolute path of the server host environment. single leanding slash accesses w.r.t. the data_dir.
        :param wd: we remove the leading slash so that //home/directory allows you to access absolute path of the server host environment. single leanding slash accesses w.r.t. the data_dir.
        :param recursive:
        :param start:
        :param stop:
        :return:
        """

        from glob import iglob
        from itertools import islice

        from ml_logger.helpers.file_helpers import CwdContext
        wd = wd[1:] if wd and wd.startswith("/") else wd
        query = query[1:] if query and query.startswith("/") else query
        with CwdContext(os.path.join(self.data_dir, wd or "")):
            file_paths = list(islice(iglob(query, recursive=recursive), start, stop))
            return file_paths

    def load(self, key, dtype, start=None, stop=None):
        """
        when key starts with a single slash as in "/debug/some-run", the leading slash is removed
        and the remaining path is pathJoin'ed with the data_dir of the server.

        So if you want to access absolute path of the filesystem that the logging server is in,
        you should append two leadning slashes. This way, when the leanding slash is removed,
        the remaining path is still an absolute value and joining with the data_dir would post
        no effect.

        "//home/ubuntu/ins-runs/debug/some-other-run" would point to the system absolute path.

        Modes:
            "read": returns the binary string.
            "read_text": returns the file's content as plain-text
            "read_pkl": reads the content of a pickle file
            "read_np": reads the content of numpy file.

        Note: We might want to do the hydration of the pickle and numpy files on the client-side.
        This way we only send the serilized data over-the-wire.

        :param key: a path string
        :param dtype: (str), one of "read", "read_text", "read_pickle", "read_np"
        :param start: end index
        :param stop: start index
        :return: None, or a tuple of each one of the data chunks logged into the file.
        """
        key = key[1:] if key.startswith("/") else key
        abs_path = os.path.join(self.data_dir, key)
        if dtype == 'read':
            try:
                with open(abs_path, 'rb') as f:
                    return f.read()
            except FileNotFoundError as e:
                return None
        elif dtype == 'read_text':
            try:
                with open(abs_path, 'r') as f:
                    return f.decode('utf-8')
            except FileNotFoundError as e:
                return None
        elif dtype == 'read_pkl':
            from .helpers import load_from_pickle
            try:
                return list(load_from_pickle(abs_path))[start:stop]
            except FileNotFoundError as e:
                return None
        elif dtype == 'read_np':
            import numpy
            try:
                return numpy.load(abs_path)
            except FileNotFoundError as e:
                return None
        elif dtype == 'read_image':
            raise NotImplementedError('reading images is not implemented.')

    def remove(self, key):
        """
        removes by key.

        :param key: the path from the logging directory.
        :return: None
        """
        abs_path = os.path.join(self.data_dir, key)
        try:
            os.remove(abs_path)
        except FileNotFoundError as e:
            return None
        except OSError as e:
            import shutil
            shutil.rmtree(abs_path)

    def log(self, key, data, dtype, options: LogOptions = None):
        """
        handler function for writing data to the server. Can be called directly.

        :param key:
        :param data:
        :param dtype:
        :param options:
        :return:
        """
        # todo: overwrite mode is not tested and not in-use.
        write_mode = "w" if options and options.overwrite else "a"
        if dtype == "log":
            abs_path = os.path.join(self.data_dir, key)
            try:
                with open(abs_path, write_mode + 'b') as f:
                    dill.dump(data, f)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                with open(abs_path, write_mode + 'b') as f:
                    dill.dump(data, f)
        if dtype == "byte":
            abs_path = os.path.join(self.data_dir, key)
            try:
                with open(abs_path, write_mode + 'b') as f:
                    f.write(data)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                with open(abs_path, write_mode + 'b') as f:
                    f.write(data)
        elif dtype.startswith("text"):
            abs_path = os.path.join(self.data_dir, key)
            try:
                with open(abs_path, write_mode + "+") as f:
                    f.write(data)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                with open(abs_path, write_mode + "+") as f:
                    f.write(data)
        elif dtype.startswith("yaml"):
            import ruamel.yaml
            if ruamel.yaml.version_info < (0, 15):
                yaml = ruamel.yaml
                StringIO = ruamel.yaml.StringIO
                load_fn = yaml.safe_load
            else:
                from ruamel.yaml import YAML, StringIO
                yaml = YAML()
                yaml.explict_start = True
                load_fn = yaml.load

            stream = StringIO()
            yaml.dump(data, stream)
            output = stream.getvalue()
            abs_path = os.path.join(self.data_dir, key)
            try:
                with open(abs_path, write_mode + "+") as f:
                    if options.write_mode == 'key':
                        d = load_fn('\n'.join(f))
                        if d is not None:
                            d.update(output)
                            output = d
                    f.write(output)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                with open(abs_path, write_mode + "+") as f:
                    if options.write_mode == 'key':
                        d = load_fn('\n'.join(f))
                        if d is not None:
                            d.update(output)
                            output = d
                    f.write(output)
        elif dtype.startswith("image"):
            abs_path = os.path.join(self.data_dir, key)
            if "." not in key:
                abs_path = abs_path + ".png"
            from PIL import Image
            assert data.dtype in ALLOWED_TYPES, "image datatype must be one of {}".format(ALLOWED_TYPES)
            if len(data.shape) == 3 and data.shape[-1] == 1:
                data.resize(data.shape[:-1])
            im = Image.fromarray(data)
            try:
                im.save(abs_path)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                im.save(abs_path)


@cli_parse
class Params:
    data_dir = Proto("/tmp/logging-server", help="The directory for saving the logs")
    port = Proto(8081, help="port for the logging server")
    host = Proto("127.0.0.1", help="IP address for running the server. Default only allows localhost from making "
                                   "requests. If you want to allow all ip, set this to '0.0.0.0'.")
    workers = Proto(1, help="Number of workers to run in parallel")
    debug = BoolFlag(False, help='boolean flag for printing out debug traces')


if __name__ == '__main__':
    import pkg_resources

    v = pkg_resources.get_distribution("ml_logger").version
    print('running ml_logger.server version {}'.format(v))
    server = LoggingServer(data_dir=Params.data_dir)
    server.serve(host=Params.host, port=Params.port, workers=Params.workers)
