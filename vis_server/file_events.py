from hachiko.hachiko import AIOEventHandler, AIOWatchdog
from asyncio import coroutine, Queue, sleep
from sanic import response
from sanic.exceptions import RequestTimeout

from vis_server.file_utils import path_match
from . import config
import json

subscriptions = []
watcher = None


class Handler(AIOEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @coroutine
    async def on_any_event(self, event):
        _event = dict(src_path=event.src_path, event_type=event.event_type, is_directory=event.is_directory)
        for que in subscriptions:
            await que.put(_event)
            # self._loop.create_task(que.put(event))


def setup_watch_queue(app, loop):
    print('setting up watch queue')
    start_watcher()
    print('watcher setup is complete!')


def start_watcher():
    global watcher

    handler = Handler()
    print('starting file watcher...')
    watcher = AIOWatchdog(config.Args.logdir, event_handler=handler)
    watcher.start()
    print('watcher start is complete')


import os


# server does not have access to a disconnect event.
# currently subscriptions only grows.
# Will add timeout based cleanup after.
async def file_events(request, file_path="", query="*"):
    q = Queue()
    subscriptions.append(q)

    async def streaming_fn(response):
        try:
            while True:
                print('subscription que started')
                file_event = await q.get()
                src_path = file_event['src_path']
                if src_path.startswith(os.path.join(config.Args.logdir, file_path)) and path_match(file_path, query):
                    file_event['src_path'] = src_path[len(config.Args.logdir):]
                print("=>>", file_event)
                response.write(f"data: {json.dumps(file_event)}\r\n\r\n".encode())
                sleep(0.1)
        # todo: this timeout doesn't really work.
        # todo: also add handling of stream is terminated logic (separate from above).
        except RequestTimeout:
            subscriptions.remove(q)

    return response.stream(streaming_fn, content_type="text/event-stream")
    # subscriptions.remove(q)
