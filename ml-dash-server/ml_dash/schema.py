from graphene import relay, ObjectType, Float, Field, Schema, AbstractType, List, String, Union

from .data import create_ship, get_empire, get_faction, get_rebels, get_ship, get_user


class Team(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='string serialized data')
    description = String(description='string serialized data')
    users = List(lambda: User)
    projects = List(lambda: Project)


class User(ObjectType):
    class Meta:
        interfaces = relay.Node,

    username = String(description='string serialized data')
    name = String(description='string serialized data')
    projects = List(lambda: Project)
    teams = List(lambda: Team)


class Project(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='string serialized data')
    description = String(description='string serialized data')
    projects = List(lambda: Project)


from graphene import lazy_import


class Binder(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description="keys in the parameter file")
    children = List("Binder", description="child binders")
    files = List(lambda: FileAndDirectory, description="keys in the parameter file")
    # date_created
    # date_modified


class Directory(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='string serialized data')
    description = String(description='string serialized data')
    children = List(lambda: FileAndDirectory)


# File Types
class File(AbstractType):
    class Meta:
        interfaces = relay.Node,

    name = String(description='string serialized data')
    description = String(description='string serialized data')


class Parameters(ObjectType, File):
    pass


class Metrics(ObjectType, File):
    """this is just the file type."""
    pass


class Image(ObjectType, File):
    pass


class Video(ObjectType, File):
    pass


class TextFile(ObjectType, File):
    pass


class BinaryFile(ObjectType, File):
    pass


class JsonFile(ObjectType, File):
    pass


class YamlFile(ObjectType, File):
    pass


class FileAndDirectory(Union):
    class Meta:
        types = (File, Parameters, Metrics, TextFile, BinaryFile, JsonFile)


class ExperimentView(ObjectType):
    class Meta:
        interfaces = relay.Node,

    charts = List(lambda: Chart)


class Point(ObjectType):
    class Meta:
        interfaces = relay.Node,

    x = Float()
    y = Float()


class LineSeries(ObjectType):
    class Meta:
        interfaces = relay.Node,
        description = "simple line series"

    data = List(lambda: Point)
    label = String(description="label for the time series")


class StdSeries(ObjectType):
    class Meta:
        interfaces = relay.Node,
        description = "line series with standard deviation"

    data = List(lambda: Point)
    label = String(description="label for the series")


class QuantileSeries(ObjectType):
    class Meta:
        interfaces = relay.Node,
        description = "line series with quantile ticks"

    data = List(lambda: Point)
    label = String(description="label for the time series")


class Series(Union):
    class Meta:
        types = (LineSeries, StdSeries, QuantileSeries)


class LineChart(ObjectType):
    class Meta:
        interfaces = relay.Node,

    time_series = List(lambda: Series)

    title = String(description="title for the chart")
    x_label = String(description="label for the x axis")
    y_label = String(description="label for the y axis")
    x_low = String(description="lower range for the x axis")
    x_high = String(description="higher range for x axis")
    y_low = String(description="lower range for y axis")
    y_high = String(description="higher range for y axis")


class ParameterDomain(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String()
    domain_low = Float()
    domain_high = Float()


class ParallelCoordinates(ObjectType):
    class Meta:
        interfaces = relay.Node,

    # todo: {key, value}
    data = List(ObjectType)
    domains = List(ParameterDomain)


class Chart(Union):
    """this is also a file type."""

    class Meta:
        types = LineChart, ParallelCoordinates


#
#
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


class Ship(ObjectType):
    """A ship in the Star Wars saga"""

    class Meta:
        interfaces = relay.Node,

    name = String(description="The name of the ship.")

    @classmethod
    def get_node(cls, info, id):
        return get_ship(id)


class ShipConnection(relay.Connection):
    class Meta:
        node = Ship


class Faction(ObjectType):
    """A faction in the Star Wars saga"""

    class Meta:
        interfaces = relay.Node,

    name = String(description="The name of the faction.")
    ships = relay.ConnectionField(
        ShipConnection, description="The ships used by the faction."
    )

    def resolve_ships(self, info, **args):
        # Transform the instance ship_ids into real instances
        return [get_ship(ship_id) for ship_id in self.ships]

    @classmethod
    def get_node(cls, info, id):
        return get_faction(id)


class IntroduceShip(relay.ClientIDMutation):
    class Input:
        ship_name = String(required=True)
        faction_id = String(required=True)

    ship = Field(Ship)
    faction = Field(Faction)

    @classmethod
    def mutate_and_get_payload(
            cls, root, info, ship_name, faction_id, client_mutation_id=None
    ):
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=ship, faction=faction)


class Query(ObjectType):
    # context?
    # todo: files
    # todo: series

    user = Field(User)
    users = Field(List(User))
    team = Field(Team)
    teams = Field(List(Team))
    project = Field(Project)
    projects = Field(List(Project))

    def resolve_user(self, username):
        return get_user(username)

    rebels = Field(Faction)
    empire = Field(Faction)
    node = relay.Node.Field()

    def resolve_rebels(self, info):
        return get_rebels()

    def resolve_empire(self, info):
        return get_empire()


class Mutation(ObjectType):
    # todo: remove_file
    # todo: rename_file
    # todo: edit_file
    # todo: move_file
    # todo: copy_file

    introduce_ship = IntroduceShip.Field()


schema = Schema(query=Query, mutation=Mutation)
