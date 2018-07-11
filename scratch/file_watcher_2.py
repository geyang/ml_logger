from collections import deque, OrderedDict
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


class Handler:
    def __init__(self, buffer=10, filter_by=lambda *_: True):
        self.buffer = FixSizeOrderedDict(maxlen=buffer)
        self.filter_fn = filter_by

    @debounce(0.1)
    def plot(self):
        clear_output(wait=True)
        for key, im in reversed(list(self.buffer.items())):
            print(im['path'], im['event_type'])
            display(im['image'])

    def dispatch(self, event):
        event_type = event.event_type
        path = event.src_path
        # print(event_type, event.src_path)
        if path.endswith('.png') and event_type != "moved" and self.filter_fn(path, event_type):
            im = Image(path)
            self.buffer[path] = dict(path=path, image=im, event_type=event_type)

            self.plot()


prefix = lambda path, *_: "plans" in path

observer = Observer()
observer.schedule(Handler(filter_by=prefix), path, recursive=True)
observer.start()
observer.join()
