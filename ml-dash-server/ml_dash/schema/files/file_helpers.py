from glob import iglob
from os import stat
from os.path import basename, join

from ml_dash.file_handlers import cwdContext


def file_stat(file_path):
    # note: this when looped over is very slow. Fine for a small list of files though.
    stat_res = stat(file_path)
    sz = stat_res.st_size
    return dict(
        name=basename(file_path),
        path=file_path,
        mtime=stat_res.st_mtime,
        ctime=stat_res.st_ctime,
        # type=ft,
        size=sz,
    )


def find_files(cwd, query, start=None, stop=None):
    from itertools import islice
    from ml_dash.config import Args
    with cwdContext(join(Args.logdir, cwd[1:])):
        file_paths = list(islice(iglob(query, recursive=True), start or 0, stop or 200))
        files = map(file_stat, file_paths)
        return files
