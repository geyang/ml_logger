import json
import mimetypes
import os
import re
import stat
from datetime import datetime
from . import config
from sanic import response


def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        type = 'dir'
    else:
        type = 'file'
    return type


async def get_path(request, file_path=""):
    as_records = request.args.get('records')
    as_json = request.args.get('json')
    as_attachment = request.args.get('download')
    is_recursive = request.args.get('recursive')
    show_hidden = request.args.get('hidden')
    query = request.args.get('query')
    start = int(request.args.get('start', '0'))
    stop = int(request.args.get('stop', '200'))

    path = os.path.join(config.Args.logdir, file_path)

    if os.path.isdir(path):
        from itertools import islice
        files = islice(list_directory(path, ".", is_recursive, show_hidden), start, stop)
        res = response.json([*files], status=200)
    elif os.path.isfile(path):
        if as_records:
            from ml_logger.helpers import load_pickle_as_dataframe
            df = load_pickle_as_dataframe(path)
            res = response.json(df.to_json(orient="records"), status=200)
        elif as_json:
            from ml_logger.helpers import load_pickle_as_dataframe
            df = load_pickle_as_dataframe(path)
            res = response.json(df.to_json(orient="records"), status=200)
        else:
            res = await response.file(path, headers={'Content-Disposition': 'attachment'})
            if as_attachment:
                res.headers.add()
    else:
        res = response.text('Not found', status=404)
    return res


def list_directory(root, current_directory, recursive=False, show_hidden=False):
    total = {'size': 0, 'dir': 0, 'file': 0}
    real_path = os.path.join(root, current_directory)
    for filename in os.listdir(real_path):
        if not show_hidden and filename.startswith('.'):
            continue
        filepath = os.path.join(root, current_directory, filename)
        stat_res = os.stat(filepath)
        ft = get_type(stat_res.st_mode)
        sz = stat_res.st_size
        info = dict(
            name=filename,
            path=os.path.join(current_directory, filename),
            mtime=stat_res.st_mtime,
            type=ft,
            size=sz,
        )
        total[ft] += 1
        total['size'] += sz
        yield info
        if recursive and info['type'] == 'dir':
            yield from list_directory(root, info['path'], recursive, show_hidden)
