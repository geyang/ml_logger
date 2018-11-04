from datetime import datetime
import os
# todo: switch to dill instead
import dill
from ruamel.yaml import YAML, StringIO
from collections import namedtuple

from params_proto import cli_parse, Proto, BoolFlag

import sanic

from ml_logger.serdes import deserialize, serialize
import numpy as np
from typing import NamedTuple, Any


class LogOptions(NamedTuple):
    overwrite: bool = None
    write_mode: str = None


class LogEntry(NamedTuple):
    key: str
    data: Any
    type: str
    options: LogOptions = None


LoadEntry = namedtuple("LoadEntry", ['key', 'type'])
RemoveEntry = namedtuple("RemoveEntry", ['key'])


class PingData(NamedTuple):
    exp_key: str
    status: Any
    burn: bool = False


Signal = namedtuple("Signal", ['exp_key', 'signal'])
ALLOWED_TYPES = (np.uint8,)  # ONLY uint8 is supported.


class LoggingServer:
    def __init__(self, data_dir):
        assert os.path.isabs(data_dir)
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        print('logging data to {}'.format(data_dir))

    configure = __init__

    def serve(self, port):
        self.app = sanic.Sanic()
        self.app.add_route(self.log_handler, '/', methods=['POST'])
        self.app.add_route(self.read_handler, '/', methods=['GET'])
        self.app.add_route(self.ping_handler, '/ping', methods=['POST'])
        self.app.add_route(self.remove_handler, '/', methods=['DELETE'])
        # todo: need a file serving url
        self.app.run(port=port, debug=Params.debug)

    def ping_handler(self, req):
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

    def read_handler(self, req):
        if not req.json:
            msg = f'request json is empty: {req.text}'
            print(msg)
            return sanic.response.text(msg)
        load_entry = LoadEntry(**req.json)
        print("loading: {} type: {}".format(load_entry.key, load_entry.type))
        res = self.load(load_entry.key, load_entry.type)
        data = serialize(res)
        return sanic.response.text(data)

    def remove_handler(self, req):
        if not req.json:
            msg = f'request json is empty: {req.text}'
            print(msg)
            return sanic.response.text(msg)
        remove_entry = RemoveEntry(**req.json)
        print("removing: {}".format(remove_entry.key))
        self.remove(remove_entry.key)
        return sanic.response.text('ok')

    def log_handler(self, req):
        if not req.json:
            print(f'request json is empty: {req.text}')
            return sanic.response.text("Reuqest json is empty")
        log_entry = LogEntry(**req.json)
        print("writing: {} type: {} options: {}".format(log_entry.key, log_entry.type, log_entry.options))
        data = deserialize(log_entry.data)
        options = log_entry.options if log_entry.options is None else LogOptions(*log_entry.options)
        self.log(log_entry.key, data, log_entry.type, options)
        return sanic.response.text('ok')

    def load(self, key, dtype):
        if dtype == 'read':
            abs_path = os.path.join(self.data_dir, key)
            try:
                with open(abs_path, 'rb') as f:
                    return f.decode('utf-8')
            except FileNotFoundError as e:
                return None
        elif dtype == 'read_text':
            abs_path = os.path.join(self.data_dir, key)
            try:
                with open(abs_path, 'r') as f:
                    return f.decode('utf-8')
            except FileNotFoundError as e:
                return None
        elif dtype == 'read_pkl':
            from .helpers import load_from_pickle
            abs_path = os.path.join(self.data_dir, key)
            try:
                return list(load_from_pickle(abs_path))
            except FileNotFoundError as e:
                return None
        elif dtype == 'read_np':
            import numpy
            abs_path = os.path.join(self.data_dir, key)
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
            yaml = YAML()
            yaml.explict_start = True
            stream = StringIO()
            yaml.dump(data, stream)
            output = stream.getvalue()
            abs_path = os.path.join(self.data_dir, key)
            try:
                with open(abs_path, write_mode + "+") as f:
                    if options.write_mode == 'key':
                        d = yaml.load('\n'.join(f))
                        if d is not None:
                            d.update(output)
                            output = d
                    f.write(output)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                with open(abs_path, write_mode + "+") as f:
                    if options.write_mode == 'key':
                        d = yaml.load('\n'.join(f))
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
    debug = BoolFlag(False, help='boolean flag for printing out debug traces')


if __name__ == '__main__':
    import pkg_resources

    v = pkg_resources.get_distribution("ml_logger").version
    print('running ml_logger.server version {}'.format(v))
    server = LoggingServer(data_dir=Params.data_dir)
    server.serve(port=Params.port)
