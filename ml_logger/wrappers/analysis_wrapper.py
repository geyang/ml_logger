def Analysis(fn, prefix="analysis", *ARGS, **KWARGS):
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

    RUN_DICT = vars(RUN)

    def thunk(*args, **kwargs):
        import time
        import traceback
        from ml_logger import logger

        RUN._update(**RUN_DICT)

        logger.configure(root=RUN.server, prefix=RUN.prefix)
        # logger.job_started(job=dict(job_id=logger.slurm_job_id), host=dict(hostname=logger.hostname), )

        with logger.Prefix(prefix):
            try:
                assert not (args and ARGS), f"can not use position argument at both thunk creation and run.\n" \
                                            f"_args: {args}\n" \
                                            f"ARGS: {ARGS}\n"
                KWARGS.update(**kwargs)

                results = fn(*args, **kwargs)

                with logger.SyncContext():  # Make sure uploaded finished before termination.
                    logger.log_line("========== execution is complete ==========")
                    logger.job_completed()
                    logger.flush()
                time.sleep(3)

            except Exception as e:
                tb = traceback.format_exc()
                with logger.SyncContext():  # Make sure uploaded finished before termination.
                    logger.print(tb, color="red")
                    logger.log_text(tb, filename="traceback.err")
                    # need to add status for ec2/slurm preemption
                    logger.job_errored()
                    logger.flush()
                time.sleep(3)
                raise e

            return results

    return thunk
