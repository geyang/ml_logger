import os
from os.path import abspath
from typing import Union

from params_proto.neo_proto import PrefixProto, Accumulant
from .caches.summary_cache import SummaryCache
from .helpers.print_utils import PrintHelper
from .log_client import LogClient
from .ml_logger import USER, ROOT, logger, LOGGER_USER, ML_Logger, pJoin
from .struts import ALLOWED_TYPES


class RUN(PrefixProto):
    """The main point of this config object is to provide a way for config functions
    to directly specify the job prefix.

    :param server: the ml-logger server address <host>:<port>
    :param username: the username for the ml-logger server
    :param project: the logging prefix for the project. Default to "scratch"

    :param job_prefix: prefix for this job
    :param job_postfix: postfix for this job
    :param job_counter: a counter. Details see below

    example:
        - job_counter == 0: sets counter to 0
        - job_counter == None: does not use counter in logging prefix.
        - job_counter == True: increment counter by "1" with each job.
    """
    server = ROOT
    username = LOGGER_USER
    project = "scratch"  # default project name

    cwd = os.getcwd()
    script_root = os.environ.get("HOME", cwd)
    script_path = None

    from datetime import datetime
    now = datetime.now().astimezone()
    prefix = "{username}/{project}/{now:%Y/%m-%d}/{file_stem}/{job_name}"
    job_name = "{job_prefix}/{job_postfix}"
    job_prefix = f'{now:%H.%M.%S}'
    job_postfix = '{job_counter}'
    job_counter = Accumulant(None)

    restart = False
    readme = None

    # noinspection PyMissingConstructor
    @classmethod
    def __init__(cls, job_counter: Union[None, bool, int] = True, **kwargs):
        cls._update(**kwargs)
        from ml_logger import logger

        script_root_depth = cls.script_root.split('/').__len__()
        script_truncated = logger.truncate(cls.script_path, depth=script_root_depth)
        cls.file_stem = logger.stem(script_truncated)

        if job_counter is None:
            pass
        elif job_counter is False:
            cls.job_counter = None
        elif cls.job_counter is None:
            cls.job_counter = 0
        # fuck python -- bool is subtype of int. Fuck guido.
        elif isinstance(job_counter, int) and not isinstance(job_counter, bool):
            cls.job_counter = job_counter
        else:
            cls.job_counter += 1

        data = vars(cls)
        while "{" in data['prefix']:
            data = {k: v.format(**data) if isinstance(v, str) else v for k, v in data.items()}

        cls.JOB_NAME = data['job_name']
        cls.PREFIX = data['prefix']


if __name__ == '__main__':
    RUN(job_counter=None)
    assert RUN.job_counter is None

    RUN()
    assert RUN.job_counter == 0

    RUN()
    assert RUN.job_counter == 1

    RUN(job_counter=True)
    assert RUN.job_counter == 2

    RUN(job_counter=0)
    assert RUN.job_counter == 0

    RUN(job_counter=10)
    assert RUN.job_counter == 10


def instr(fn, *ARGS, __file=False, __silent=False, **KWARGS):
    """
    Instrumentation thunk factory for configuring the logger.

    :param fn: function to be called
    :param *ARGS: position arguments for the call
    :param __file__: console mode, by-pass file related logging
    :param __silent: do not print
    :param **KWARGS: keyword arguments for the call
    :return: a thunk that can be called without parameters
    """
    import inspect
    from termcolor import cprint
    from ml_logger import logger, ROOT, USER, pJoin

    if __file:
        caller_script = pJoin(os.getcwd(), __file)
    else:
        launch_module = inspect.getmodule(inspect.stack()[1][0])
        __file = launch_module.__file__
        caller_script = abspath(__file)

    # note: for scripts in the `plan2vec` module this also works -- b/c we truncate fixed depth.
    RUN(script_path=caller_script)

    ROOT = RUN.server
    PREFIX = RUN.PREFIX

    # todo: there should be a better way to log these.
    # todo: we shouldn't need to log to the same directory, and the directory for the run shouldn't be fixed.
    logger.configure(root=RUN.server, prefix=PREFIX, asynchronous=False,  # use sync logger
                     max_workers=4, register_experiment=False)
    if RUN.restart:
        with logger.Sync():
            logger.remove(".")
    logger.upload_file(caller_script)
    # the tension is in between creation vs run. Code snapshot are shared, but runs need to be unique.
    _ = dict()
    if ARGS:
        _['args'] = ARGS
    if KWARGS:
        _['kwargs'] = KWARGS

    logger.log_params(
        run=logger.run_info(status="created", script_path=RUN.script_path,
                            script_root=RUN.script_root),
        revision=logger.rev_info(),
        fn=logger.fn_info(fn),
        **_,
        silent=__silent)

    logger.print('taking diff, if this step takes too long, check if your '
                 'uncommitted changes are too large.', color="green")
    logger.diff()
    if RUN.readme:
        logger.log_text(RUN.readme, "README.md", dedent=True)

    import jaynes  # now set the job name to prefix
    if jaynes.RUN.config and jaynes.RUN.mode != "local":
        runner_class, runner_args = jaynes.RUN.config['runner']
        runner_args['name'] = pJoin(RUN.file_stem, RUN.JOB_NAME)
        from jaynes import runners
        if runner_class is runners.Docker:
            runner_args['name'] = runner_args['name'].replace('/', '-')

        del logger, jaynes, runner_args, runner_class
        if not __file:
            cprint(f'Set up job name', "green")

    def thunk(*args, **kwargs):
        import traceback
        from ml_logger import logger

        assert not (args and ARGS), \
            f"can not use position argument at both thunk creation as well as run.\n" \
            f"_args: {args}\n" \
            f"ARGS: {ARGS}\n"

        logger.configure(root=ROOT, prefix=PREFIX, register_experiment=False, max_workers=10)
        logger.log_params(host=dict(hostname=logger.hostname),
                          run=dict(status="running", startTime=logger.now(), job_id=logger.job_id))

        import time
        try:
            _KWARGS = {**KWARGS}
            _KWARGS.update(**kwargs)

            results = fn(*(args or ARGS), **_KWARGS)

            logger.log_line("========== execution is complete ==========")
            logger.log_params(run=dict(status="completed", completeTime=logger.now()))
            logger.flush()
            time.sleep(3)
        except Exception as e:
            tb = traceback.format_exc()
            with logger.SyncContext():  # Make sure uploaded finished before termination.
                logger.print(tb, color="red")
                logger.log_text(tb, filename="traceback.err")
                logger.log_params(run=dict(status="error", exitTime=logger.now()))
                logger.flush()
            time.sleep(3)
            raise e

        return results

    return thunk
