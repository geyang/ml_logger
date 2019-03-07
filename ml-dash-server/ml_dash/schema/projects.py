from os import listdir
from os.path import isfile, join, split

from graphene import ObjectType, relay, String, List
from ml_dash import schema


class Project(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the project')

    # description = String(description='string serialized data')
    # experiments = List(lambda: schema.Experiments)

    experiments = relay.ConnectionField(lambda: schema.experiments.ExperimentConnection)

    def resolve_experiments(self, info, **kwargs):
        return schema.experiments.find_experiments(cwd=self.id)

    directories = relay.ConnectionField(lambda: schema.directories.DirectoryConnection)
    files = relay.ConnectionField(lambda: schema.files.FileConnection)

    def resolve_directories(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.Directory(id=join(self.id, _), name=_)
                for _ in listdir(root_dir) if not isfile(join(root_dir, _))]

    def resolve_files(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.Directory(id=join(self.id, _), name=_)
                for _ in listdir(root_dir) if isfile(join(root_dir, _))]

    # def resolve_experiments(self, info, **kargs):
    #     from ml_dash.config import Args
    #     root_dir = join(Args.logdir, self.id[1:])
    #
    #     return [schema.Directory(id=join(self.id, _), name=_)
    #             for _ in listdir(root_dir) if isfile(join(root_dir, _))]

    @classmethod
    def get_node(cls, info, id):
        return get_project(id)


class ProjectConnection(relay.Connection):
    class Meta:
        node = Project


def get_projects(username):
    import os
    from ml_dash.config import Args
    user_root = join(Args.logdir, username)
    return [Project(name=_, id=join('/', username, _))
            for _ in os.listdir(user_root) if not isfile(_)]


def get_project(id):
    from ml_dash.config import Args
    path = join(Args.logdir, id[1:])
    return Project(id=id, name=split(id[1:])[1], _path=path)
