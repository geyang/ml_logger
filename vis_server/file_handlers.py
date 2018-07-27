import os
import stat
from glob import iglob
from pathlib import Path

from shutil import rmtree

from vis_server.file_utils import path_match
from . import config
from sanic import response


def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        type = 'dir'
    else:
        type = 'file'
    return type


async def remove_path(request, file_path=""):
    print(file_path)
    path = os.path.join(config.Args.logdir, file_path)
    if os.path.isdir(path):
        rmtree(path)
        res = response.text("ok", status=204)
    elif os.path.isfile(path):
        os.remove(path)
        res = response.text("ok", status=204)
    else:
        res = response.text('Not found', status=404)
    return res


from contextlib import contextmanager


@contextmanager
def cwd(path):
    owd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(owd)


async def get_path(request, file_path=""):
    print(file_path)

    as_records = request.args.get('records')
    as_json = request.args.get('json')
    as_log = request.args.get('log')
    as_attachment = int(request.args.get('download', '0'))
    is_recursive = request.args.get('recursive')
    show_hidden = request.args.get('hidden')
    query = request.args.get('query', "*").strip()
    start = int(request.args.get('start', '0'))
    stop = int(request.args.get('stop', '200'))
    reservoir_k = int(request.args.get('reservoir', '200'))

    # limit for the search itself.
    search_limit = 500

    path = os.path.join(config.Args.logdir, file_path)
    print("=============>", [query], [path], os.path.isdir(path))

    if os.path.isdir(path):
        from itertools import islice
        with cwd(path):
            print(os.getcwd(), query, is_recursive)
            file_paths = list(islice(iglob(query, recursive=is_recursive), start, stop))
            files = map(file_stat, file_paths)
            res = response.json(files, status=200)
    elif os.path.isfile(path):
        if as_records:
            from ml_logger.helpers import load_pickle_as_dataframe
            df = load_pickle_as_dataframe(path, reservoir_k)
            res = response.text(df.to_json(orient="records"), status=200, content_type='application/json')
        elif as_log:
            from ml_logger.helpers import load_pickle_as_dataframe
            df = load_pickle_as_dataframe(path, reservoir_k)
            res = response.text(df.to_json(orient="records"), status=200, content_type='application/json')
        elif as_json:
            from ml_logger.helpers import load_from_pickle
            data = [_ for _ in load_from_pickle(path)]
            res = response.json(data, status=200, content_type='application/json')
        else:
            # todo: check the file handling here. Does this use correct mimeType for text files?
            res = await response.file(path)
            if as_attachment:
                res.headers['Content-Disposition'] = 'attachment'
    else:
        res = response.text('Not found', status=404)
    return res


# use glob! LOL
def file_stat(file_path):
    # this looped over is very slow. Fine for a small list of files though.
    stat_res = os.stat(file_path)
    ft = get_type(stat_res.st_mode)
    sz = stat_res.st_size
    return dict(
        name=os.path.basename(file_path),
        path=file_path,
        mtime=stat_res.st_mtime,
        ctime=stat_res.st_ctime,
        type=ft,
        size=sz,
    )
