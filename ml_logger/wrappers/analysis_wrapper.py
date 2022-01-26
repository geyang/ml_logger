def Analysis(fn, prefix="analysis", *args, **kwargs):
    """
    Analysis wrapper for dumping the results into an analysis folder

    Args:
        fn: the analysis function to be called
        exp: the experiment prefix
        prefix: the prefix for the analysis folder
        *args: positional arguments to be passed to the analysis function
        **kwargs: keyword arguments to be passed to the analysis function

    Returns: returns of the function `fn`
    """
    from ml_logger import RUN

    vars_RUN = vars(RUN)

    def thunk():
        from ml_logger import logger, RUN

        RUN._update(**vars_RUN)

        logger.configure(prefix=RUN.prefix)
        with logger.Prefix(prefix):
            return fn(*args, **kwargs)

    return thunk
