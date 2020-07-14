from datetime import datetime
from functools import reduce
from collections.abc import Sequence
from os.path import expanduser, join
from pprint import pprint

from termcolor import cprint
from tqdm import tqdm
from more_itertools import chunked, interleave

from ml_dash.schema.files.file_helpers import find_files, read_pickle_for_json
from ml_dash.config import Args
from ml_dash.schema.helpers import assign, dot_flatten

DEBUG = False


def type_string(obj):
    if isinstance(obj, str):
        # todo: intelligent mapping for numbers etc from strings.
        try:  # https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html
            _ = datetime.strptime(obj, "%Y-%m-%d %H:%M:%S.%f").isoformat()
            return "date", _
        except:
            return "string", obj
    elif isinstance(obj, bool):
        return "boolean", obj
    elif isinstance(obj, int):
        return "long", obj
    elif isinstance(obj, float):
        return "float", obj
    elif isinstance(obj, datetime):
        return "date", obj.isoformat()
    elif obj is None:
        return "null", True
    return None, obj


def typify(obj):
    t_str, obj = type_string(obj)
    if t_str:
        return {t_str: obj}
    elif isinstance(obj, Sequence):
        return reduce(assign, [typify(item) for item in obj], {})
    elif isinstance(obj, dict):
        return {k: typify(v) for k, v in obj.items()}


if __name__ == "__main__":
    Args.logdir = expanduser("~/runs")
    cwd = expanduser("~/runs")
    # _ = find_experiments(cwd=)
    parameter_files = find_files(cwd, "*/**/parameters.pkl", stop=500 if DEBUG else None, show_progress=True)
    print(len(parameter_files))

    from elasticsearch import Elasticsearch

    es = Elasticsearch([dict(host='localhost', port=9200)])

    response = es.indices.delete(index='ml-dash', ignore=[400, 404])
    cprint('deleted the index', 'green')

    # note: how th nested index works
    #  https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html
    response = es.indices.create(
        index="ml-dash",
        body=dict(mappings=dict(
            dynamic=False,
            _source=dict(excludes=["index.*"]),
            properties={
                "data": dict(type="object", enabled=False),
                "index": {
                    "type": "nested",
                    "enabled": True,
                    "properties": {
                        "key": {"type": "keyword", },
                        "string": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 2014}
                            }
                        },
                        "boolean": {"type": "boolean"},
                        "date": {"type": "date",
                                 "format": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"},
                        "long": {"type": "long"},
                        "float": {"type": "float"},
                        "null": {"type": "boolean", "null_value": False}
                    }
                }
            }
        )))

    for chunk in tqdm(chunked(parameter_files, 1000), desc="Uploading..."):
        parameters = [reduce(assign, [
            *(read_pickle_for_json(join(cwd, f['path'])) or []), {"dir": f['dir']}
        ]) for f in chunk]
        actions = [{"index": dict(_id=p['dir'], )} for p in parameters]
        documents = [dict(index=[dict(key=k, **v) for k, v in typify(dot_flatten(p)).items()], **p)
                     for p in parameters]

        # documents[0]

        # https://stackoverflow.com/questions/20288770/how-to-use-bulk-api-to-store-the-keywords-in-es-by-using-python
        response = es.bulk(index='ml-dash', body=interleave(actions, documents))

        if response['errors']:
            for i, item in enumerate(response['items']):
                if item['index']['status'] >= 300:
                    print(item['index'])
                    print(documents[i])
                    break

    cprint('finished', 'green')
