from os.path import split
from graphene import ObjectType, relay, String
from ml_dash import schema


class Parameter(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the directory')

    # description = String(description='string serialized data')
    # experiments = List(lambda: schema.Experiments)

    @classmethod
    def get_node(cls, info, id):
        return get_parameters(id)


class ParameterConnection(relay.Connection):
    class Meta:
        node = Parameter


def get_parameters(id):
    # path = os.path.join(Args.logdir, id[1:])
    return Parameter(id=id, name=split(id[1:])[1])
