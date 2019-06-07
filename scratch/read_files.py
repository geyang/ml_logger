from functools import reduce
from os.path import expanduser, join
from tqdm import tqdm
from more_itertools import chunked
from pprint import pprint

from ml_dash.schema.files.file_helpers import find_files, read_json
from ml_dash.config import Args
from ml_dash.schema.helpers import assign

DEBUG = True


if __name__ == "__main__":
    Args.logdir = expanduser("~/runs")
    cwd = expanduser("~/runs")
    # _ = find_experiments(cwd=)
    parameter_files = find_files(cwd, "*/**/parameters.pkl", stop=10 if DEBUG else None, show_progress=True)
    print(len(parameter_files))

    for chunk in tqdm(chunked(parameter_files, 1000)):
        parameters = [
            reduce(assign, [*(read_json(join(cwd, f['path'])) or []), dict(_id=f['dir'])]) for f in chunk]
        indices = [dict(index=dict(_id=p['dir'])) for p in parameters]
        pprint(chunk[0])

if __name__ == "__main__":
    from elasticsearch import Elasticsearch

    es = Elasticsearch([dict(host='localhost', port=9200)])
    # es.index(index="ml-dash", doc_type="experiment", id=)
