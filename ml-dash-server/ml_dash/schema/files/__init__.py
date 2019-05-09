import os
from os.path import split, isabs, realpath, join, basename, dirname
from graphene import ObjectType, relay, String, Int, Mutation, ID, Field, Node, Boolean
from graphene.types.generic import GenericScalar
from graphql_relay import from_global_id
from ml_dash.schema.files.file_helpers import find_files

from . import parameters, metrics


class File(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='name of the directory')
    stem = String(description="stem of the file name")

    def resolve_stem(self, info, ):
        return self.name.split('.')[0]

    path = String(description='path to the file')
    rel_path = String(description='relative path to the file')
    text = String(description='text content of the file',
                  start=Int(required=False, default_value=0),
                  stop=Int(required=False, default_value=None))

    def resolve_text(self, info, start=0, stop=None):
        from ml_dash.config import Args
        with open(join(Args.logdir, self.id[1:]), "r") as f:
            lines = list(f)[start: stop]
            return "".join(lines)

    json = GenericScalar(description="the json content of the file")

    def resolve_json(self, info):
        import json
        try:
            from ml_dash.config import Args
            with open(join(Args.logdir, self.id[1:]), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    yaml = GenericScalar(description="the content of the file using yaml")

    def resolve_yaml(self, info):
        import ruamel.yaml
        if ruamel.yaml.version_info < (0, 15):
            yaml = ruamel.yaml
            load_fn = yaml.safe_load
        else:
            from ruamel.yaml import YAML
            yaml = YAML()
            yaml.explict_start = True
            load_fn = yaml.load

        from ml_dash.config import Args
        with open(join(Args.logdir, self.id[1:]), "r") as f:
            return load_fn('\n'.join(f))

    @classmethod
    def get_node(cls, info, id):
        return get_file(id)


class FileConnection(relay.Connection):
    class Meta:
        node = File


def get_file(id):
    return File(id=id, name=basename(id[1:]))


def find_files_by_query(cwd, query="**/*.*", **kwargs):
    from ml_dash.config import Args
    assert isabs(cwd), "the current work directory need to be an absolute path."
    _cwd = realpath(join(Args.logdir, cwd[1:])).rstrip('/')
    parameter_files = find_files(_cwd, query)
    return [
        # note: not sure about the name.
        File(id=join(cwd.rstrip('/'), p['path']),
             name=basename(p['path']),
             path=join(cwd.rstrip('/'), p['path']),
             rel_path=p['path'], )
        for p in parameter_files
    ]


def glob_files(cwd, query="*.*"):
    return find_files_by_query(cwd=cwd, query=query)


def save_text_to_file(path, text):
    from ml_dash.config import Args
    assert isabs(path), "the path has to be absolute path."
    _path = join(Args.logdir, path[1:])
    with open(_path, "w") as f:
        f.write(text)
    return get_file(path)


def save_yaml_to_file(path, data):
    from ml_dash.config import Args
    assert isabs(path), "the path has to be absolute path."
    _path = join(Args.logdir, path[1:])
    # note: assume all text format
    with open(_path, "w+") as f:
        import yaml
        _ = yaml.dump(data, f)
    return get_file(path)


def save_json_to_file(path, data):
    from ml_dash.config import Args
    assert isabs(path), "the path has to be absolute path."
    _path = join(Args.logdir, path[1:])
    # note: assume all text format
    with open(_path, "w+") as f:
        import json
        _ = json.dumps(data, sort_keys=True, indent=2)
        f.write(_)
    return get_file(path)


def remove_file(path):
    """remove does not work with directories"""
    from ml_dash.config import Args
    assert isabs(path), "the path has to be absolute path."
    _path = join(Args.logdir, path[1:])
    os.remove(_path)


def remove_directory(path):
    """rmtree does not work with files"""
    import shutil
    from ml_dash.config import Args
    assert isabs(path), "the path has to be absolute path."
    _path = join(Args.logdir, path[1:])
    shutil.rmtree(_path)


class MutateTextFile(relay.ClientIDMutation):
    class Input:
        id = ID()
        text = String(required=True)

    file = Field(File)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, text, client_mutation_id):
        _type, path = from_global_id(id)
        return MutateTextFile(file=save_text_to_file(path, text))


class MutateYamlFile(relay.ClientIDMutation):
    """
    serializes the data to a yaml file format
    """
    class Input:
        id = ID()
        data = GenericScalar()

    file = Field(File)

    @classmethod
    def mutate_and_get_payload(self, root, info, id, data, client_mutation_id):
        _type, path = from_global_id(id)
        return MutateYamlFile(file=save_yaml_to_file(path, data))


class MutateJSONFile(relay.ClientIDMutation):
    """
    serializes the data to a json file format
    """
    class Input:
        id = ID()
        data = GenericScalar()

    file = Field(File)

    @classmethod
    def mutate_and_get_payload(self, root, info, id, data, client_mutation_id):
        _type, path = from_global_id(id)
        return MutateJSONFile(file=save_json_to_file(path, data))


class DeleteFile(relay.ClientIDMutation):
    class Input:
        id = ID()

    ok = Boolean()
    id = ID()

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id):
        _type, path = from_global_id(id)
        try:
            remove_file(path)
            return DeleteFile(ok=True, id=id)
        except FileNotFoundError:
            return DeleteFile(ok=False)


class DeleteDirectory(relay.ClientIDMutation):
    class Input:
        id = ID()

    ok = Boolean()
    id = ID()

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id):
        _type, path = from_global_id(id)
        try:
            remove_directory(path)
            return DeleteDirectory(ok=True, id=id)
        except FileNotFoundError:
            return DeleteDirectory(ok=False)
