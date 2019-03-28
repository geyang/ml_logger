from ml_dash.schema import schema
from sanic_graphql import GraphQLView

from .file_events import file_events, setup_watch_queue
from .file_handlers import get_path, remove_path, batch_get_path

from sanic import Sanic
from sanic_cors import CORS

app = Sanic(__name__)
# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}}, automatic_options=True)

# @app.listener('before_server_start')
# def init_graphql(app, loop):
#     app.add_route(GraphQLView.as_view(schema=schema, executor=AsyncioExecutor(loop=loop)), '/graphql')

# new graphQL endpoints
app.add_route(GraphQLView.as_view(schema=schema, graphiql=True), '/graphql',
              methods=['GET', 'POST', 'FETCH', 'OPTIONS'])
app.add_route(GraphQLView.as_view(schema=schema, batch=True), '/graphql/batch',
              methods=['GET', 'POST', 'FETCH', 'OPTIONS'])

# # Serving static app
# app.add_route(get_path, '/*', methods=['GET', 'OPTIONS'])

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
    from . import config
    from termcolor import cprint

    if logdir:
        config.Args.logdir = logdir

    cprint("launched server with config:", "green")
    cprint("Args:", 'yellow')
    print(vars(config.Args))
    cprint("Sanic Server Args:", 'yellow')
    print(vars(config.ServerArgs))

    config.ServerArgs.update(**kwargs)
    app.run(**vars(config.ServerArgs))


if __name__ == "__main__":
    # see: https://sanic.readthedocs.io/en/latest/sanic/deploying.html
    # call this as `python -m ml_logger.main`
    run()
