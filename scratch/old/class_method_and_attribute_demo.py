class G:
    log_dir = None

    def __init__(self, log_dir=None):
        if log_dir:
            self.log_dir = log_dir

    configure = __init__


g = G()

assert g.log_dir is None
g.configure(log_dir='hey')
assert g.log_dir == "hey"
