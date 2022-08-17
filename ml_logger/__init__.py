import os
import sys
from os.path import abspath

from params_proto import PrefixProto, Accumulant, Proto, Flag
from termcolor import colored

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

    script_root = Proto(os.getcwd(), env="HOME")
    script_path = None

    now = logger.now()
    prefix = "{username}/{project}/{now:%Y/%m-%d}/{file_stem}/{job_name}"
    job_name = Proto(f"{now:%H.%M.%S}/{{job_counter}}", help="""
        Default to '{now:%H.%M.%S}'. use '{now:%H.%M.%S}/{job_counter}'
        for multiple launches. You can do so by setting:

        ```python
        RUN.job_name += "/{job_counter}"

        for params in sweep:
           thunk = instr(main)
           jaynes.run(thun)
        jaynes.listen()
        ```
        """)
    job_counter = Accumulant(0, help="Default to 0. Use True to increment by 1.")

    resume = Proto(True, help="whether starting the run from scratch, or "
                              "resume previous checkpoints")
    readme = None

    debug = Flag(default="pydevd" in sys.modules, help="set to True automatically for pyCharm")
    CUDA_VISIBLE_DEVICES = None

    # noinspection PyMissingConstructor
    @classmethod
    def __new__(cls, deps=None, script_path=None, __count=True, **kwargs):
        from ml_logger import logger

        sr = cls.script_root
        script_root_depth = str(sr.value if isinstance(sr, Proto) else sr).split('/').__len__()
        script_truncated = logger.truncate(os.path.abspath(script_path), depth=script_root_depth)

        file_stem = logger.stem(script_truncated)

        if __count and (isinstance(cls.job_counter, int) or isinstance(cls.job_counter, float)):
            cls.job_counter += 1

        data = vars(cls)
        data.update(kwargs)
        while "{" in data['prefix']:
            data = {k: v.format(file_stem=file_stem, **data) if isinstance(v, str) else v for k, v in data.items()}

        return data['prefix'], data['job_name'], file_stem


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


def instr(fn, *ARGS, __file=False, __create_job=True, __count=True, __silent=False, **KWARGS):
    """
    Instrumentation thunk factory for configuring the logger.

    :param fn: function to be called
    :param ARGS: position arguments for the call
    :param __file: str, console mode, by-pass file related logging
    :param __create_job: bool, default to True, set to False when you are relaunching
    :param __count: bool, increase the RUN.job_counter by 1 on each `instr` call.
    :param __silent: bool, do not print
    :param KWARGS: keyword arguments for the call
    :return: a thunk that can be called without parameters
    """
    import inspect
    from termcolor import cprint
    from ml_logger import logger, pJoin

    if __file:
        caller_script = pJoin(os.getcwd(), __file)
    else:
        launch_module = inspect.getmodule(inspect.stack()[1][0])
        __file = launch_module.__file__
        caller_script = abspath(__file)

    # need to set the deps
    # note: for scripts in the `plan2vec` module this also works -- b/c we truncate fixed depth.
    PREFIX, JOB_NAME, FILE_STEM = RUN(script_path=caller_script, _RUN__count=__count)

    RUN_DICT = vars(RUN)
    RUN_DICT['prefix'] = PREFIX
    RUN_DICT['job_name'] = JOB_NAME
    RUN_DICT['file_stem'] = FILE_STEM

    # todo: there should be a better way to log these.
    # todo: we shouldn't need to log to the same directory, and the directory for the run shouldn't be fixed.
    logger.configure(root=RUN.server, prefix=PREFIX, asynchronous=False,  # use sync logger
                     max_workers=4)
    if __create_job:
        # # this is debatable
        # if RUN.restart:
        #     with logger.Sync():
        #         logger.remove(".")
        logger.upload_file(caller_script)

        # the tension is in between creation vs run. Code snapshot are shared, but runs need to be unique.
        logger.job_created(
            job=dict(script_path=RUN.script_path, script_root=RUN.script_root,
                     counter=RUN.job_counter, prefix=RUN.prefix, name=RUN.job_name),
            revision=logger.rev_info(),
            fn=logger.fn_info(fn),
            args=ARGS,
            kwargs=KWARGS)

        logger.print('taking diff, if this step takes too long, check if your uncommitted changes are '
                     'too large.', color="green")
        logger.diff()
        if RUN.readme:
            logger.log_text(RUN.readme, "README.md", dedent=True)

    try:
        import jaynes  # now set the job name to prefix

        if jaynes.Jaynes.mode not in [False, 'local']:
            assert jaynes.Jaynes.launcher, "Make sure you call jaynes.config first."

            # gcp requires lower-case and less than 60 characters
            # fixme: change all non alpha-numeric and non "-" characters to "-".
            launch_name = USER + "-" + PREFIX[-61 + len(USER):].replace('/', '-').replace('_', '-') \
                .replace('.', '-').lower()
            runner_name = launch_name

            if RUN.CUDA_VISIBLE_DEVICES is not None:
                extended_envs = jaynes.Jaynes.runner_config[1][
                                    'envs'] + f" CUDA_VISIBLE_DEVICES={RUN.CUDA_VISIBLE_DEVICES}"
                jaynes.Jaynes.config(jaynes.Jaynes.mode,
                                     launch={'name': launch_name},
                                     runner={'name': runner_name, 'envs': extended_envs})
            else:
                jaynes.Jaynes.config(jaynes.Jaynes.mode,
                                     launch={'name': launch_name},
                                     runner={'name': runner_name})

            del jaynes
            if not __file:
                cprint(f'Set up job name', "green")

    except ModuleNotFoundError:
        pass

    del logger

    def thunk(*args, **kwargs):
        import traceback
        from ml_logger import logger

        RUN._update(**RUN_DICT)
        if RUN.CUDA_VISIBLE_DEVICES is not None:
            visibility = os.environ.get('CUDA_VISIBLE_DEVICES', None)
            assert RUN.CUDA_VISIBLE_DEVICES == visibility, \
                f"CUDA_VISIBLE_DEVICES={visibility}. Expected {RUN.CUDA_VISIBLE_DEVICES}"

        logger.configure(root=RUN.server, prefix=PREFIX, max_workers=10)
        # todo logger.job_id is specific to slurm
        logger.job_started(job=dict(job_id=logger.slurm_job_id), host=dict(hostname=logger.hostname), )

        import time
        try:
            assert not (args and ARGS), f"can not use position argument at both thunk creation and run.\n" \
                                        f"_args: {args}\n" \
                                        f"ARGS: {ARGS}\n"

            _KWARGS = {**KWARGS}
            _KWARGS.update(**kwargs)

            results = fn(*(args or ARGS), **_KWARGS)

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


def is_stale(time_str, threshold=5.):
    """Helper function for time lapsed

    :param time_str: the runTime string from logger job.runTime
    :param threshold: in minutes
    :return: boolean value whether time has passed.
    """
    if time_str is None:
        return False

    from datetime import datetime

    time_elapsed = logger.utcnow() - datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    minutes_since = time_elapsed.total_seconds() / 60.
    return minutes_since > threshold


def needs_relaunch(prefix, stale_limit=5., silent=False, not_exist_ok=False, *args, **kwargs):
    """

    :param prefix: the prefix for the experiment entry.
    :param stale_limit: the stale limit in minutes. Shared for all job status.
    :param silent: default to False. When truful, silences the printout.
    :param not_exist_ok: default to False b/c this error message is helpful.
    :param args: extended parameters for printing.
    :return: bool needs relaunch
    """
    # make sure that the prefix context is set to absolute path
    if not prefix.startswith('/'):
        prefix = "/" + prefix

    with logger.Prefix(prefix):
        status, request_time, request_id, region, run_time, start_time, create_time = \
            logger.read_params('job.status', 'job.requestTime', 'job.request_id', 'job.region', 'job.runTime',
                               'job.startTime', 'job.createTime', default=None, not_exist_ok=not_exist_ok)
    stale = relaunch = False
    if status is None:
        s = colored("not exist", 'red'), f"https://app.dash.ml{prefix}"
        relaunch = True
    elif status == "completed":
        s = colored(status, 'green'), f"https://app.dash.ml{prefix}"
    elif status == "created":
        s = colored(status, 'yellow'), f"https://app.dash.ml{prefix}"
        stale = is_stale(create_time, stale_limit)
    elif status == "requested":
        s = colored(status, 'yellow'), f"https://app.dash.ml{prefix}"
        stale = is_stale(request_time, stale_limit)
    elif status == "started":
        s = colored(status, 'yellow'), f"https://app.dash.ml{prefix}"
        stale = is_stale(start_time, stale_limit)
    elif status == "errored":
        s = colored(status, 'red'), f"https://app.dash.ml{prefix}"
        relaunch = True
    elif status == "running":
        s = colored(status, 'yellow'), f"https://app.dash.ml{prefix}"
        stale = is_stale(run_time, stale_limit)
    else:
        s = status,

    if not silent:
        print(*s, colored("is stale", "red") if stale else None, *[a for a in args if a], **kwargs)

    return stale or relaunch


def memoize(f):
    l = ML_Logger(".cache", root=os.getcwd())
    c_path = f"{f.__module__}.{f.__name__}.pkl"
    cache = l.load_pkl(c_path)
    memo = cache[0] if cache else {}

    def wrapper(*args, **kwargs):
        key = (*args, *kwargs.keys(), *kwargs.values())
        if key not in memo:
            memo[key] = f(*args, **kwargs)
            l.save_pkl(memo, c_path)
        return memo[key]

    return wrapper
