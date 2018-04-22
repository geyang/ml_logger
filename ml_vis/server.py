import os
import pickle
from collections import namedtuple
from params_proto import cli_parse, Proto
from ml_vis.serdes import deserialize

LogEntry = namedtuple("LogEntry", ['key', 'data', 'type'])


class LoggingServer:
    def __init__(self, data_dir):
        assert os.path.isabs(data_dir)
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def serve(self, port):
        from japronto import Application
        self.app = Application()
        self.app.router.add_route('/', self.log_handler, method='POST')
        self.app.run(port=port, debug=True)

    def log_handler(self, req):
        self.log(req.json)
        return req.Response(text='ok')

    def log(self, entry):
        log_entry = LogEntry(**entry)

        if log_entry.type == "log":
            abs_path = os.path.join(self.data_dir, log_entry.key)
            try:
                with open(abs_path, 'ab') as f:
                    pickle.dump(log_entry.data, f)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                with open(abs_path, 'ab') as f:
                    pickle.dump(log_entry.data, f)
        elif log_entry.type.startswith("text"):
            abs_path = os.path.join(self.data_dir, log_entry.key)
            if "." not in log_entry.key:
                abs_path = abs_path + ".md"
            with open(abs_path, "a") as f:
                f.write(log_entry.data)
        elif log_entry.type.startswith("image"):
            abs_path = os.path.join(self.data_dir, log_entry.key)
            if "." not in log_entry.key:
                abs_path = abs_path + ".png"
            from PIL import Image
            data = deserialize(log_entry.data)
            im = Image.fromarray(data)
            try:
                im.save(abs_path)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(abs_path))
                im.save(abs_path)
        elif log_entry.type.startswith("video"):
            # todo: mpeg can be appended directly, making it a nice format.
            raise NotImplementedError



@cli_parse
class Params:
    data_dir = Proto("/tmp/logging-server", help="The directory for saving the logs")
    port = Proto(8081, help="port for the logging server")


if __name__ == '__main__':
    server = LoggingServer(data_dir=Params.data_dir)
    server.serve(port=Params.port)
