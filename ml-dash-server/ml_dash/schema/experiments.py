from os import listdir
from os.path import isfile, join, split, basename, dirname, realpath

from graphene import ObjectType, relay, String, Field
from ml_dash import schema
from ml_dash.schema import files
from ml_dash.schema.files.file_helpers import find_files


class Experiment(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the directory')
    parameters = Field(lambda: files.parameters.Parameters, )
    metrics = Field(lambda: files.metrics.Metrics, )

    def resolve_parameters(self, info):
        return files.parameters.get_parameters(self.parameters)

    def resolve_metrics(self, info):
        # todo: find metric files
        return files.metrics.get_metrics(self.id)

    # description = String(description='string serialized data')
    # experiments = List(lambda: schema.Experiments)
    # children = List(lambda: schema.ExperimentAndFiles)

    directories = relay.ConnectionField(lambda: schema.directories.DirectoryConnection)
    files = relay.ConnectionField(lambda: schema.files.FileConnection)

    def resolve_directories(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.Experiment(id=join(self.id, _), name=_)
                for _ in listdir(root_dir) if not isfile(join(root_dir, _))]

    def resolve_files(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.Experiment(id=join(self.id, _), name=_)
                for _ in listdir(root_dir) if isfile(join(root_dir, _))]

    @classmethod
    def get_node(cls, info, id):
        return get_directory(id)


class ExperimentConnection(relay.Connection):
    class Meta:
        node = Experiment


def get_directory(id):
    # path = os.path.join(Args.logdir, id[1:])
    return Experiment(id=id, name=split(id[1:])[1])


def find_experiments(cwd, **kwargs):
    from ml_dash.config import Args
    cwd = realpath(join(Args.logdir, cwd[1:]))
    parameter_files = find_files(cwd, "**/parameters.pkl", **kwargs)
    return [
        # note: not sure about the name.
        Experiment(id=join(cwd, p['dir']), name=basename(p['dir']), parameters=join(cwd, p['path']), )
        for p in parameter_files
    ]
