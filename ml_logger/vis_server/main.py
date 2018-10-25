from . import config
from .file_events import file_events, setup_watch_queue, start_watcher
from .file_handlers import get_path, remove_path, batch_get_path

from sanic import Sanic
from sanic_cors import CORS, cross_origin

app = Sanic(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

app.add_route(get_path, '/files/', methods=['GET', 'OPTIONS'])
app.add_route(get_path, '/files/<file_path:path>', methods=['GET', 'OPTIONS'])
app.add_route(batch_get_path, '/batch-files', methods=['GET', 'OPTIONS'])
app.add_route(remove_path, '/files/<file_path:path>', methods=['DELETE'])
app.add_route(file_events, '/file-events', methods=['GET', 'OPTIONS'])
app.add_route(file_events, '/file-events/<file_path:path>', methods=['GET', 'OPTIONS'])
app.listener('before_server_start')(setup_watch_queue)


# app.add_task(start_watcher)

def run(logdir=None, **kwargs):
    import os
    config.ServerArgs.update(**kwargs)
    if logdir:
        config.Args.logdir = os.path.realpath(logdir)

    assert os.path.isabs(config.Args.logdir), "the processed log_dir has to start with '/'."
    app.run(**vars(config.ServerArgs))


if __name__ == "__main__":
    run()
