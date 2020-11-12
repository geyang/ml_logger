import pathlib
from glob import iglob
from os import stat
from os.path import basename, join, realpath, dirname

from ml_dash.file_handlers import cwdContext


def file_stat(file_path, no_stat=True):
    """
    getting the stats of the file.

    no_stat turns the stat call off.

    :param file_path:
    :param no_stat:
    :return:
    """
    # note: this when looped over is very slow. Fine for a small list of files though.
    if no_stat:
        return dict(
            name=basename(file_path),
            path=file_path,
            dir=dirname(file_path),
        )

    stat_res = stat(file_path)
    sz = stat_res.st_size
    return dict(
        name=basename(file_path),
        path=file_path,
        dir=dirname(file_path),
        time_modified=stat_res.st_mtime,
        time_created=stat_res.st_ctime,
        # type=ft,
        size=sz,
    )


def fast_glob(query, wd, skip_children=False):
    """
    ignore subtree when file is found under a certain directory.
    :param skip_childre:
    :return:
    """
    raise NotImplementedError()


def find_files(cwd, query, start=None, stop=None, no_stat=True, show_progress=False):
    """
    find files by iGlob.

    :param cwd: the context folder for the glob, excluded from returned path list.
    :param query: glob query
    :param start: starting index for iGlob.
    :param stop: ending index for iGlob
    :param no_stat: boolean flag to turn off the file_stat call.
    :return:
    """
    from itertools import islice

    # https://stackoverflow.com/a/58126417/1560241
    if query.endswith('**'):
        query += "/*"

    with cwdContext(cwd):
        _ = islice(pathlib.Path(".").glob(query), start, stop)
        if show_progress:
            from tqdm import tqdm
            _ = tqdm(_, desc="@find_files")
        for i, file in enumerate(_):
            print(str(file))
            yield file_stat(str(file), no_stat=no_stat)


def read_dataframe(path, k=None):
    from ml_logger.helpers import load_pickle_as_dataframe
    try:
        return load_pickle_as_dataframe(path, k)
    except FileNotFoundError:
        return None


def read_records(path, k=200):
    from ml_logger.helpers import load_pickle_as_dataframe
    df = load_pickle_as_dataframe(path, k)
    return df.to_json(orient="records")


def read_log(path, k=200):
    from ml_logger.helpers import load_pickle_as_dataframe
    df = load_pickle_as_dataframe(path, k)
    return df.to_json(orient="records")


def read_pikle(path):
    from ml_logger.helpers import load_from_pickle
    data = [_ for _ in load_from_pickle(path)]
    return data


def read_pickle_for_json(path):
    """convert non JSON serializable types to string"""
    from ml_logger.helpers import load_from_pickle, regularize_for_json
    data = [regularize_for_json(_) for _ in load_from_pickle(path)]
    return data


def read_text(path, start, stop):
    from itertools import islice
    with open(path, 'r') as f:
        text = ''.join([l for l in islice(f, start, stop)])
    return text


def read_binary():
    raise NotImplementedError()
    # todo: check the file handling here. Does this use correct
    #  mimeType for text files?
    # res = await response.file(path)
    # if as_attachment:
    #     res.headers['Content-Disposition'] = 'attachment'
