from graphene import relay, ObjectType, Float, Schema, List, String, Field
from ml_dash.schema.files.series import Series, get_series, SeriesArguments
from ml_dash.schema.files.metrics import Metrics, get_metrics
from ml_dash.schema.schema_helpers import bind, bind_args
from ml_dash.schema.users import User, get_users, get_user
from ml_dash.schema.projects import Project
from ml_dash.schema.directories import Directory, get_directory
from ml_dash.schema.files import File, FileConnection, MutateTextFile, MutateJSONFile, MutateYamlFile, \
    DeleteFile, DeleteDirectory, glob_files
# MutateJSONFile, MutateYamlFile
from ml_dash.schema.experiments import Experiment


# class Experiment(graphene.ObjectType):
#     class Meta:
#         interfaces = relay.Node,
#
#     parameter_keys = graphene.List(description="keys in the parameter file")
#     metric_keys = graphene.List(description="the x data")
#     video_keys = graphene.List(description="the x data")
#     img_keys = graphene.List(description="the x data")
#     diff_keys = graphene.List(description="the x data")
#     log_keys = graphene.List(description="the x data")
#     view_config = ""
#
# class TimeSeries(graphene.ObjectType):
#     class Meta:
#         interfaces = relay.Node,
#
#     x_data = graphene.List(description="the x data")
#     y_data = graphene.List(description="the y data")
#     serialized = graphene.String(description='string serialized data')
#
#
# class TimeSeriesWithStd(graphene.ObjectType):
#     class Meta:
#         interfaces = relay.Node,
#
#     x_data = graphene.List(description="the x data")
#     y_data = graphene.List(description="the y data")
#     std_data = graphene.List(description="the standard deviation data")
#     quantile_25_data = graphene.List(description="the standard deviation data")
#     quantile_50_data = graphene.List(description="the standard deviation data")
#     quantile_75_data = graphene.List(description="the standard deviation data")
#     quantile_100_data = graphene.List(description="the standard deviation data")
#     mode_data = graphene.List(description="the standard deviation data")
#     mean_data = graphene.List(description="the standard deviation data")
#     serialized = graphene.String(description='string serialized data')
#
#
# class LineChart(graphene.ObjectType):
#     class Meta:
#         interfaces = relay.Node,
#
#     key = graphene.String(description="The path to the metrics file (including metrics.pkl)")
#     x_key = graphene.String(description="key for the x axis")
#     x_label = graphene.String(description="label for the x axis")
#     y_key = graphene.String(description="key for the y axis")
#     y_label = graphene.String(description="label for the x axis")


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

    glob = Field(List(File), cwd=String(required=True), query=String(), resolver=bind_args(glob_files))


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
