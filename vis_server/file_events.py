from hachiko.hachiko import AIOEventHandler, AIOWatchdog
from asyncio import coroutine, Queue, sleep
from sanic import response
from . import config

subscriptions = []
watcher = None


class Handler(AIOEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @coroutine
    async def on_any_event(self, event):
        for que in subscriptions:
            await que.put(event)
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


# server does not have access to a disconnect event.
# currently subscriptions only grows.
# Will add timeout based cleanup after.
async def file_events(request):
    q = Queue()
    subscriptions.append(q)

    async def streaming_fn(response):
        try:
            while True:
                print('subscription que started')
                file_event = await q.get()
                print("=>>", file_event)
                response.write(file_event.src_path)
                sleep(0.1)
        except RequestTimeout:
            subscriptions.remove(q)

    return response.stream(streaming_fn)
    # subscriptions.remove(q)
