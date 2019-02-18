def bind(fn):
    """
    Binds the function to the class.

    :param fn:
    :return: bound_fn
    """
    return lambda _, *args, **kwargs: fn(*args, **kwargs)


def bind_args(fn):
    """
    Binds args after info.

    :param fn:
    :return: bound_fn
    """
    return lambda _, info, *args, **kwargs: fn(*args, **kwargs)

