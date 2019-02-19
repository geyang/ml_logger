from functools import reduce
from os.path import split, join
from graphene import ObjectType, relay, String, List
from graphene.types.generic import GenericScalar
from ml_dash import schema
from ml_dash.config import Args
from ml_dash.schema.files.file_helpers import read_json
from ml_dash.schema.helpers import assign, dot_keys, dot_flatten


class Parameters(ObjectType):
    class Meta:
        interfaces = relay.Node,

    _path = String(description="The true path to the parameter file. Internal use only")
    keys = List(String, description="list of parameter keys")
    value = GenericScalar(description="the json value for the parameters")
    raw = GenericScalar(description="the raw data object for the parameters")
    flat = GenericScalar(description="the raw data object for the parameters")

    def resolve_keys(self, info):
        value = reduce(assign, read_json(join(Args.logdir, self.id[1:])) or [{}])
        return dot_keys(value)

    def resolve_value(self, info, **kwargs):
        return reduce(assign, read_json(join(Args.logdir, self.id[1:])) or [{}])

    def resolve_raw(self, info, **kwargs):
        return read_json(join(Args.logdir, self.id[1:]))

    def resolve_flat(self, info, **kwargs):
        value = reduce(assign, read_json(join(Args.logdir, self.id[1:])) or [{}])
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
    # path = os.path.join(Args.logdir, id[1:])
    return Parameters(id=id)
