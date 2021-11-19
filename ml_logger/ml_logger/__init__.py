import os
import sys
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

    script_root = Proto(os.getcwd(), env="HOME")
    script_path = None

    now = logger.now()
    prefix = "{username}/{project}/{now:%Y/%m-%d}/{file_stem}/{job_name}"
    job_name = Proto(f"{now:%H.%M.%S}",
                     help="""
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

    debug = Proto("pydevd" in sys.modules, help="set to True automatically for pyCharm")

    # noinspection PyMissingConstructor
    @classmethod
    def __new__(cls, deps=None, script_path=None, **kwargs):
        from ml_logger import logger

        sr = cls.script_root
        script_root_depth = (sr.value if isinstance(sr, Proto) else sr).split('/').__len__()
        script_truncated = logger.truncate(os.abspath(script_path), depth=script_root_depth)

        file_stem = logger.stem(script_truncated)

        if isinstance(cls.job_counter, int) or isinstance(cls.job_counter, float):
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
    PREFIX, JOB_NAME, FILE_STEM = RUN(script_path=caller_script)

    RUN_DICT = vars(RUN)
    RUN_DICT['prefix'] = PREFIX
    RUN_DICT['job_name'] = JOB_NAME
    RUN_DICT['file_stem'] = FILE_STEM

    # todo: there should be a better way to log these.
    # todo: we shouldn't need to log to the same directory, and the directory for the run shouldn't be fixed.
    logger.configure(root=RUN.server, prefix=PREFIX, asynchronous=False,  # use sync logger
                     max_workers=4)
    if not __dryrun:
        # # this is debatable
        # if RUN.restart:
        #     with logger.Sync():
        #         logger.remove(".")
        logger.upload_file(caller_script)

        # the tension is in between creation vs run. Code snapshot are shared, but runs need to be unique.
        logger.job_created(
            job=dict(script_path=RUN.script_path, script_root=RUN.script_root, counter=RUN.job_counter,
                     prefix=RUN.prefix, name=RUN.job_name),
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

        launch_args = jaynes.RUN.config['launch']
        runner_class, runner_args = jaynes.RUN.config['runner']

        # gcp requires lower-case and less than 60 characters
        launch_args['name'] = PREFIX[-60:].replace('/', '-').replace('_', '-').lower()
        runner_args['name'] = PREFIX
        if runner_class is jaynes.runners.Docker:
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
        logger.configure(root=RUN.server, prefix=PREFIX, max_workers=10)
        # todo logger.job_id is specific to slurm
        logger.job_started(job=dict(job_id=logger.slurm_job_id), host=dict(hostname=logger.hostname), )

        import time
        try:
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
