from glob import iglob
from os import stat
from os.path import basename, join, realpath, dirname

from ml_dash.file_handlers import cwdContext


def file_stat(file_path):
    # note: this when looped over is very slow. Fine for a small list of files though.
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


def find_files(cwd, query, start=None, stop=None):
    """
    find files by iGlob.

    :param cwd: the context folder for the glob, excluded from returned path list.
    :param query: glob query
    :param start: starting index for iGlob.
    :param stop: ending index for iGlob
    :return:
    """
    from itertools import islice
    with cwdContext(cwd):
        file_paths = list(islice(iglob(query, recursive=True), start, stop))
        files = [file_stat(_) for _ in file_paths]
        return files


def read_dataframe(path, k=200):
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


def read_json(path):
    from ml_logger.helpers import load_from_pickle
    data = [_ for _ in load_from_pickle(path)]
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
