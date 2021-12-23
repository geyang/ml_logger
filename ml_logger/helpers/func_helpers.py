from typing import List, Any


def assign(d1, d2):
    if not d2:
        return d1
    for k, v in d2.items():
        if isinstance(d1.get(k, None), dict):
            d1[k] = assign(d1[k], v)
        else:
            d1[k] = v
    return d1


if __name__ == "__main__":
    object1 = {"a": 1, "b": 2, "c": 3}
    object2 = assign({"c": 4, "d": 5}, object1)
    assert object2['c'] == 3
    assert object2['d'] == 5


def idot_keys(d, strict=True):
    for k, v in d.items():
        if isinstance(v, dict):
            if not strict:
                yield k
            for _ in idot_keys(v, strict):
                yield k + "." + _
        else:
            yield k


def dot_keys(d, strict=True):
    return [*idot_keys(d, strict)]


if __name__ == "__main__":
    object = {"a": 1, "b": 2, "c": 3, "child": {"a": 3, "grandchild": {'d': 8}}}
    assert dot_keys(object) == ['a', 'b', 'c', 'child.a', 'child.grandchild.d']
    assert dot_keys(object, strict=False) == ['a', 'b', 'c', 'child', 'child.a', 'child.grandchild',
                                              'child.grandchild.d']


def idot_flatten(d, ancestors: List[Any] = tuple()):
    """
    returns a flattened dictionary with the keys of the nexted dictionaries converted into dot-separated keys.

    :param d: map
    :return: flat map
    """
    for k, v in d.items():
        if isinstance(v, dict):
            for _k, _v in idot_flatten(v):
                yield k + "." + _k, _v
        else:
            yield k, v


def dot_flatten(d):
    # note: dictionaries are ordered by default in python 3.7.
    return dict(idot_flatten(d))


def dot_unflatten(d):
    root = {}
    for k, v in d.items():
        current = root
        *parents, key = k.split(".")
        for parent in parents:
            if parent not in current:
                current[parent] = {}
            current = current[parent]
        current[key] = v
    return root


if __name__ == "__main__":
    object = {"a": 1, "b": 2, "c": 3, "child": {"a": 3, "grandchild": {'d': 8}}}
    flattened = dot_flatten(object)
    assert list(flattened.keys()) == ['a', 'b', 'c', 'child.a', 'child.grandchild.d']
    recovered = dot_unflatten(flattened)
    print(recovered)

    assert dot_unflatten(flattened) == object
