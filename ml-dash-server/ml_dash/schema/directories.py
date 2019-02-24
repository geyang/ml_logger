from os import listdir
from os.path import isfile, join, split

from graphene import ObjectType, relay, String, List, Field
from graphql_relay import to_global_id, from_global_id
from ml_dash import schema
from ml_dash.schema import files


class Directory(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the directory')
    _path = String(description='internal path on the server')

    experiments = relay.ConnectionField(lambda: schema.experiments.ExperimentConnection)

    def resolve_experiments(self, info, **kwargs):
        return schema.experiments.find_experiments(cwd=self.id)

    directories = relay.ConnectionField(lambda: schema.directories.DirectoryConnection)

    def resolve_directories(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.Directory(id=join(self.id, _), name=_)
                for _ in listdir(root_dir) if not isfile(join(root_dir, _))]

    files = relay.ConnectionField(lambda: schema.files.FileConnection)

    def resolve_files(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.Directory(id=join(self.id, _), name=_)
                for _ in listdir(root_dir) if isfile(join(root_dir, _))]

    @classmethod
    def get_node(cls, info, id):
        return get_directory(id)


class DirectoryConnection(relay.Connection):
    class Meta:
        node = Directory


def get_directory(id):
    from ml_dash.config import Args
    return Directory(id=id, name=split(id[1:])[-1], _path=join(Args.logdir, id[1:]))
