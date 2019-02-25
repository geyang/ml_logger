from os import listdir
from os.path import isfile, join, split
from graphene import ObjectType, relay, String
from ml_dash import schema


class Directory(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the directory')
    path = String(description='absolute path of the directory')

    experiments = relay.ConnectionField(lambda: schema.experiments.ExperimentConnection)

    def resolve_experiments(self, info, **kwargs):
        return schema.experiments.find_experiments(cwd=self.id)

    directories = relay.ConnectionField(lambda: schema.directories.DirectoryConnection)

    def resolve_directories(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [get_directory(join(self.id, _))
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
    _id = id.rstrip('/')
    return Directory(id=_id, name=split(_id[1:])[-1], path=_id)
