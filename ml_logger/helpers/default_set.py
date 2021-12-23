class DefaultSet(set):
    def __init__(self, *items):
        """DefaultSet, a set that `reset()`s to the original elements:

        Usage:

        .. code-block:: python

            default_set = DefaultSet("first_default_item", "second_item")
            default_set.reset() # => DefaultSet({"first_default_item", "second_item"})

        :param * items: list of items (as positional arguments) as default for the set.
        """
        super().__init__()
        self._default_set = items

    def reset(self):
        self.clear()
        self.update(self._default_set)

    # def __repr__(self):
    #     return f"{self._default_set}"


if __name__ == "__main__":
    s = DefaultSet('this', '0')

    s.reset()
    assert "this" in s, "should contain original elements"

    s.add('yo')
    assert 'yo' in s, "new key"

    s.add('__yo')
    assert '__yo' in s, "new key"

    s.add('__timestamp')
    assert '__timestamp' in s, "timestamp"

    assert 'not' not in s, "not in s"

    s.clear()
    assert not s, "s should be empty after clear()"
    print('all tests pass!')
