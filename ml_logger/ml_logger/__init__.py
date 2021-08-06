import os, sys
from os.path import abspath

from params_proto.neo_proto import PrefixProto, Accumulant, Proto

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

    cwd = Proto(env="CWD")
    script_root = Proto(cwd, env="HOME")
    script_path = None

    now = logger.now()
    prefix = "{username}/{project}/{now:%Y/%m-%d}/{file_stem}/{job_name}"
    job_name = Proto(f"{now:%H.%M.%S}",
                     help="Default to '{now:%H.%M.%S}'. use '{now:%H.%M.%S}/{job_counter}'"
                          " for multiple launches.")
    job_counter = Accumulant(None)

    resume = Proto(True, help="whether starting the run from scratch, or "
                              "resume previous checkpoints")
    readme = None

    debug = Proto("pydevd" in sys.modules, help="set to True automatically for pyCharm")

    # noinspection PyMissingConstructor
    @classmethod
    def __init__(cls, deps=None, script_path=None, **kwargs):
        cls._update(deps, script_path=script_path, **kwargs)
        from ml_logger import logger

        sr = cls.script_root
        script_root_depth = (sr.value if isinstance(sr, Proto) else sr).split('/').__len__()
        script_truncated = logger.truncate(script_path, depth=script_root_depth)
        cls.file_stem = logger.stem(script_truncated)

        job_counter = cls.job_counter
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
        cls.JOB_NAME = data['job_name']


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


def instr(fn, *ARGS, __file=False, __silent=False, __dryrun=False, **KWARGS):
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

    # need to set the deps
    # note: for scripts in the `plan2vec` module this also works -- b/c we truncate fixed depth.
    RUN(script_path=caller_script)

    RUN_DICT = vars(RUN)

    # todo: there should be a better way to log these.
    # todo: we shouldn't need to log to the same directory, and the directory for the run shouldn't be fixed.
    logger.configure(root=RUN.server, prefix=RUN.PREFIX, asynchronous=False,  # use sync logger
                     max_workers=4)
    if not __dryrun:
        # # this is debatable
        # if RUN.restart:
        #     with logger.Sync():
        #         logger.remove(".")
        logger.upload_file(caller_script)

        # the tension is in between creation vs run. Code snapshot are shared, but runs need to be unique.
        logger.job_created(
            job=dict(script_path=RUN.script_path, script_root=RUN.script_root),
            revision=logger.rev_info(),
            fn=logger.fn_info(fn),
            args=ARGS,
            kwargs=KWARGS)

        logger.print('taking diff, if this step takes too long, check if your uncommitted changes are too large.',
                     color="green")
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

        assert not (args and ARGS), f"can not use position argument at both thunk creation and run.\n" \
                                    f"_args: {args}\n" \
                                    f"ARGS: {ARGS}\n"

        RUN._update(**RUN_DICT)
        logger.configure(root=RUN.server, prefix=RUN.PREFIX, max_workers=10)
        # todo logger.job_id is specific to slurm
        logger.job_started(job=dict(job_id=logger.slurm_job_id), host=dict(hostname=logger.hostname), )

        import time
        try:
            _KWARGS = {**KWARGS}
            _KWARGS.update(**kwargs)

            results = fn(*(args or ARGS), **_KWARGS)

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
