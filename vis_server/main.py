from . import config
from .file_events import file_events, setup_watch_queue, start_watcher
from .file_handlers import get_path

from sanic import Sanic
from sanic_cors import CORS, cross_origin

app = Sanic(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.add_route(get_path, '/files/', methods=['GET'])
app.add_route(get_path, '/files/<path:file_path>', methods=['GET'])
app.add_route(file_events, '/file-events', methods=['GET'])
app.listener('before_server_start')(setup_watch_queue)
# app.add_task(start_watcher)


def run(logdir=None, **kwargs):
    import os
    config.ServerArgs.update(**kwargs)
    if logdir:
        config.Args.logdir = os.path.realpath(logdir)
    app.run(**vars(config.ServerArgs))


if __name__ == "__main__":
    run()
