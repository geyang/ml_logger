from graphene import relay, ObjectType, Float, Schema, List, String, Field, Int
from ml_dash.schema.files.series import Series, get_series, SeriesArguments
from ml_dash.schema.files.metrics import Metrics, get_metrics
from ml_dash.schema.schema_helpers import bind, bind_args
from ml_dash.schema.users import User, get_users, get_user
from ml_dash.schema.projects import Project
from ml_dash.schema.directories import Directory, get_directory
from ml_dash.schema.files import File, FileConnection, MutateTextFile, MutateJSONFile, MutateYamlFile, \
    DeleteFile, DeleteDirectory, find_files_by_query
# MutateJSONFile, MutateYamlFile
from ml_dash.schema.experiments import Experiment


class EditText(relay.ClientIDMutation):
    class Input:
        text = String(required=True, description='updated content for the text file')

    text = String(description="the updated content for the text file")

    @classmethod
    def mutate_and_get_payload(cls, root, info, text, ):
        return dict(text=text)


class Query(ObjectType):
    node = relay.Node.Field()
    # context?
    # todo: files
    # todo: series

    users = Field(List(User), resolver=bind_args(get_users))
    user = Field(User, username=String(), resolver=bind_args(get_user))
    series = Field(Series, resolver=bind_args(get_series), **SeriesArguments)

    project = relay.Node.Field(Project)
    experiment = relay.Node.Field(Experiment)
    metrics = relay.Node.Field(Metrics)
    directory = relay.Node.Field(Directory)
    file = relay.Node.Field(File)

    glob = Field(List(File), cwd=String(required=True), query=String(), start=Int(), stop=Int(),
                 resolver=bind_args(find_files_by_query))


class Mutation(ObjectType):
    # todo: create_file
    # done: edit_file
    # done: remove_file
    # todo: move_file
    # todo: copy_file

    # do we need to have separate deleteDirectory? (look up relay client-side macros)

    delete_file = DeleteFile.Field()
    delete_directory = DeleteDirectory.Field()
    # update_text = EditText.Field()
    update_text = MutateTextFile.Field()
    update_json = MutateJSONFile.Field()
    update_yaml = MutateYamlFile.Field()


schema = Schema(query=Query, mutation=Mutation)
