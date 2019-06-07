from flask import jsonify, Response
from . import config
from vis_server.file_watcher import setup_file_watcher
from gevent import queue, sleep, spawn

subscriptions = []


def push_notification(event):
    e = dict(src_path=event.src_path, event_type=event.event_type, is_directory=event.is_directory)
    print(event.src_path)
    def fn():
        for que in subscriptions:
            que.put(e)

    spawn(fn)


print(config.Args.logdir)

file_watcher = setup_file_watcher(config.Args.logdir, push_notification)


# two ways to go about this:
# 1. instantiate new watcher on each request
# 2. pool requests.
def file_events():
    from .sse import ServerSentEvent
    import os, re
    from flask import request

    cwd = request.args.get('cwd', '')
    pattern = request.args.get('query', '.*\..*')
    regex = re.compile(pattern)

    q = queue.Queue()
    subscriptions.append(q)

    # file_watcher = setup_file_watcher(context_root, push_notification, patterns)
    def gen():
        try:
            ev = ServerSentEvent('ok')
            yield ev.encode()

            while True:
                print('.', end='')
                event = q.get()
                print('+', end='')
                src_path = event['src_path']
                if src_path.startswith(cwd) and src_path.match(regex):
                    ev = ServerSentEvent(src_path)
                    yield ev.encode()
        except GeneratorExit:  # Or maybe use flask signals
            subscriptions.remove(q)
            # file_watcher = setup_file_watcher(context_root, push_notification, patterns)
            # file_watcher.stop()

    r = Response(gen(), mimetype="text/event-stream")
    r.headers['Access-Control-Allow-Origin'] = "*"
    r.headers['Access-Control-Allow-Methods'] = 'GET'
    return r
