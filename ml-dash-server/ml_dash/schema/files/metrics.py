from os.path import split, realpath, join, splitext, basename
from graphene import relay, ObjectType, String, List, JSONString, Int
from graphene.types.generic import GenericScalar
from ml_dash.config import Args
from ml_dash.schema.files.file_helpers import find_files, read_records, read_dataframe


class Metrics(ObjectType):
    class Meta:
        interfaces = relay.Node,

    path = String(description="path to the file")
    name = String(description="path to the file")
    stem = String(description="stem of the file name")

    def resolve_path(self, info):
        return self.id

    def resolve_stem(self, info, ):
        return self.name.split('.')[0]

    keys = List(String, description="list of keys for the metrics")

    # value = List(GenericScalar, description="the raw value")
    value = GenericScalar(description="The value of the metrics file",
                          keys=List(String),
                          k=Int(required=False),
                          last=Int(required=False),
                          window=Int(required=False))

    def resolve_keys(self, info):
        df = read_dataframe(join(Args.logdir, self.id[1:]))
        keys = df.dropna().keys()
        return list(keys)

    # todo: add more complex queries.
    def resolve_value(self, info, keys=None, k=None, last=None, window=None):
        path = join(Args.logdir, self.id[1:])
        realpath(path)
        _ = read_dataframe(path)
        if keys:
            df = _[keys].dropna()
            return {k: df[k].values.tolist() for k in keys}
        else:
            df = _.dropna()
            return {k: v.values.tolist() for k, v in df.items()}

    @classmethod
    def get_node(cls, info, id):
        return Metrics(id, )


class MetricsConnection(relay.Connection):
    class Meta:
        node = Metrics


def get_metrics(id):
    return Metrics(id=id, name=basename(id[1:]))


def find_metrics(cwd, **kwargs):
    from ml_dash.config import Args
    _cwd = realpath(join(Args.logdir, cwd[1:]))
    parameter_files = find_files(_cwd, "**/metrics.pkl", **kwargs)
    for p in parameter_files:
        yield Metrics(id=join(cwd, p['path']), name="metrics.pkl")
