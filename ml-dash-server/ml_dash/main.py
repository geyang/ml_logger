from ml_dash.data import setup
from ml_dash.schema import schema
from sanic_graphql import GraphQLView

from . import config
from .file_events import file_events, setup_watch_queue
from .file_handlers import get_path, remove_path, batch_get_path

from sanic import Sanic
from sanic_cors import CORS

app = Sanic(__name__)
# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}}, automatic_options=True)

# for debug, sets up dummy dataset
setup()
# new graphQL endpoints
app.add_route(GraphQLView.as_view(schema=schema, graphiql=True), '/graphql',
              methods=['GET', 'POST', 'FETCH', 'OPTIONS'])
app.add_route(GraphQLView.as_view(schema=schema, batch=True), '/graphql/batch',
              methods=['GET', 'POST', 'FETCH', 'OPTIONS'])

# @app.listener('before_server_start')
# def init_graphql(app, loop):
#     app.add_route(GraphQLView.as_view(schuema=schema, execuor=AsyncioExecutor(loop=loop)), '/graphql')


# old RPC endpoints
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
    # see: https://sanic.readthedocs.io/en/latest/sanic/deploying.html
    # app.run(host='0.0.0.0', port=1337, workers=4)
    run()
