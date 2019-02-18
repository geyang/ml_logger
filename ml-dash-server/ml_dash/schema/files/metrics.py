from os.path import split
from graphene import ObjectType, relay, String
from ml_dash import schema


class File(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the directory')

    # description = String(description='string serialized data')
    # experiments = List(lambda: schema.Experiments)

    @classmethod
    def get_node(cls, info, id):
        return get_file(id)


class FileConnection(relay.Connection):
    class Meta:
        node = File


def get_file(id):
    # path = os.path.join(Args.logdir, id[1:])
    return File(id=id, name=split(id[1:])[1])
