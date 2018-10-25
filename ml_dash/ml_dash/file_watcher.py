# from . import config
import asyncio
from hachiko.hachiko import AIOWatchdog


class Handler:
    def dispatch(self, *args, **kwargs):
        print(args, kwargs)

@asyncio.coroutine
def watch_fs(path):
    watch = AIOWatchdog(path, event_handler=Handler())
    watch.start()
    while True:
        yield from asyncio.sleep(10)
    watch.stop()



if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(watch_fs("/Users/ge/machine_learning/berkeley-playground/ins-runs"))
    # asyncio.get_event_loop().run_until_complete(watch_fs("."))
    path = "."
    watch = AIOWatchdog(path, event_handler=Handler())
    watch.start()
    import time
    print('watch is setup')
    while True:
        time.sleep(10)

