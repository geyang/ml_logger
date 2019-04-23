from os import listdir
from os.path import isfile, join, basename, realpath, isabs, split

from graphene import ObjectType, relay, String, Field
from ml_dash import schema
from ml_dash.schema import files
from ml_dash.schema.files.file_helpers import find_files
from ml_dash.schema.files.metrics import find_metrics


class Experiment(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the directory')
    path = String(description="path to the experiment")

    readme = Field(lambda: schema.files.File)
    parameters = Field(lambda: files.parameters.Parameters, )
    metrics = Field(lambda: files.metrics.Metrics)

    def resolve_readme(self, info, *args, **kwargs):
        # note: keep it simple, just use README for now.
        readmes = schema.files.find_files_by_query(cwd=self.id, query="README.md")
        return readmes[0] if readmes else None

    def resolve_parameters(self, info):
        return files.parameters.get_parameters(self.parameters)

    def resolve_metrics(self, info):
        for m in find_metrics(self.id):
            return m
        return None

    directories = relay.ConnectionField(lambda: schema.directories.DirectoryConnection)
    files = relay.ConnectionField(lambda: schema.files.FileConnection)

    def resolve_directories(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.directories.get_directory(join(self.id, _))
                for _ in listdir(root_dir) if not isfile(join(root_dir, _))]

    def resolve_files(self, info, **kwargs):
        from ml_dash.config import Args
        root_dir = join(Args.logdir, self.id[1:])
        return [schema.files.File(id=join(self.id, _), name=_)
                for _ in listdir(root_dir) if isfile(join(root_dir, _))]

    @classmethod
    def get_node(cls, info, id):
        return get_experiment(id)


class ExperimentConnection(relay.Connection):
    class Meta:
        node = Experiment


def find_experiments(cwd, **kwargs):
    from ml_dash.config import Args
    assert isabs(cwd), "the current work directory need to be an absolute path."
    _cwd = realpath(join(Args.logdir, cwd[1:])).rstrip('/')
    parameter_files = find_files(_cwd, "**/parameters.pkl", **kwargs)
    return [
        # note: not sure about the name.
        Experiment(id=join(cwd.rstrip('/'), p['dir']),
                   name=basename(p['dir']) or ".",
                   path=join(cwd.rstrip('/'), p['dir']),
                   parameters=join(cwd.rstrip('/'), p['path']), )
        for p in parameter_files
    ]


def get_experiment(id):
    _id = id.rstrip('/')
    return Experiment(id=_id, name=split(_id[1:])[-1], path=_id)
