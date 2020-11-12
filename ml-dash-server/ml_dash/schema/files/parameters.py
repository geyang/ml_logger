from functools import reduce
from os.path import split, join as pJoin, basename, realpath
from graphene import ObjectType, relay, String, List
from graphene.types.generic import GenericScalar
from ml_dash.config import Args
from ml_dash.schema.files.file_helpers import find_files, read_pickle_for_json
from ml_dash.schema.helpers import assign, dot_keys, dot_flatten


class Parameters(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description="The true path to the parameter file. Internal use only")
    path = String(description="The true path to the parameter file. Internal use only")
    keys = List(String, description="list of parameter keys")
    value = GenericScalar(description="the json value for the parameters")
    raw = GenericScalar(description="the raw data object for the parameters")
    flat = GenericScalar(description="the raw data object for the parameters")

    def resolve_name(self, info):
        return basename(self.id)

    def resolve_path(self, info):
        return self.id

    def resolve_keys(self, info):
        value = reduce(assign, read_pickle_for_json(pJoin(Args.logdir, self.id[1:])) or [{}])
        return dot_keys(value)

    def resolve_value(self, info, **kwargs):
        return reduce(assign, read_pickle_for_json(pJoin(Args.logdir, self.id[1:])) or [{}])

    def resolve_raw(self, info, **kwargs):
        return read_pickle_for_json(pJoin(Args.logdir, self.id[1:]))

    def resolve_flat(self, info, **kwargs):
        # note: this always gives truncated some-folder/arameter.pkl path.
        value = reduce(assign, read_pickle_for_json(pJoin(Args.logdir, self.id[1:])) or [{}])
        return dot_flatten(value)

    # description = String(description='string serialized data')
    # experiments = List(lambda: schema.Experiments)

    @classmethod
    def get_node(cls, info, id):
        return get_parameters(id)


class ParameterConnection(relay.Connection):
    class Meta:
        node = Parameters


def get_parameters(id):
    return Parameters(id=id)


def find_parameters(cwd, **kwargs):
    from ml_dash.config import Args
    _cwd = realpath(pJoin(Args.logdir, cwd[1:]))
    parameter_files = find_files(_cwd, "parameters.pkl", **kwargs)
    for p in parameter_files:
        yield Parameters(id=pJoin(cwd, p['path']))
