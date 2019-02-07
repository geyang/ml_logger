class KeyValueCache:
    def __init__(self):
        """ key-value cache for the logger. This one allows one to overwrite old values with new ones. """
        self.data = dict()

    def __bool__(self):
        """Returns Trueness of the data dictionary."""
        return bool(self.data)

    def update(self, key_values=None, **kwargs):
        if key_values is not None:
            self.data.update(key_values)
        for k, v in kwargs.items():
            self.data[k].append(v)

    def pop_all(self):
        _ = self.data.copy()
        self.data.clear()
        return _

    def clear(self):
        self.data.clear()
