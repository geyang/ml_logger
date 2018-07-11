from gevent.pywsgi import WSGIServer
from flask_cors import CORS
from flask import Flask, make_response, request, session, render_template, send_file, Response, jsonify

from . import config
from .file_events import file_events
from .file_handlers import get_path

app = Flask(__name__, static_url_path='/assets', static_folder='assets')
CORS(app, resources={r"/*": {"origins": "*"}})

app.add_url_rule('/files/', view_func=get_path)
app.add_url_rule('/files/<path:file_path>', view_func=get_path)
app.add_url_rule('/file-events', view_func=file_events)

def run(**kwargs):
    import os
    config.Args.update(**kwargs)
    config.Args.logdir = os.path.realpath(config.Args.logdir)
    server = WSGIServer(('127.0.0.1', config.Args.port), app)
    server.serve_forever()


if __name__ == "__main__":
    print('====*****')
    run()
