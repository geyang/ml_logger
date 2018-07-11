import logging
import os
import signal

import watchdog.events
import watchdog.observers.polling
import watchdog_gevent


# https://github.com/Bogdanp/dramatiq/blob/master/dramatiq/__main__.py
def setup_file_watcher(path, callback, use_polling=False):
    """Sets up a background thread that watches for source changes and
    automatically sends SIGHUP to the current process whenever a file
    changes.
    """
    if use_polling:
        observer_class = watchdog.observers.polling.PollingObserver
    else:
        observer_class = watchdog_gevent.Observer

    file_event_handler = watchdog.events.PatternMatchingEventHandler(patterns=['*.py'])
    # file_event_handler = watchdog.events.FileSystemEventHandler()
    # monkey patching is perfectly fine.
    file_event_handler.on_any_event = callback

    # start the watcher
    file_watcher = observer_class()
    file_watcher.schedule(file_event_handler, path, recursive=True)
    print("000000000000000000000000")
    file_watcher.start()
    print("&&&&&&&&&&&&&&&&&&&&&&&&")
    return file_watcher


if __name__ == "__main__":
    """runs this in debugger to see file changes."""
    import gevent


    def cb(event):
        print(event)


    file_watcher = setup_file_watcher('.', cb)
    while True:
        gevent.sleep(1)

    file_watcher.stop()
    file_watcher.join()
