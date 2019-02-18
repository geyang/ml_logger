from graphene import relay, ObjectType, Float, Schema, AbstractType, List, String, Union, Field


# class Team(ObjectType):
#     class Meta:
#         interfaces = relay.Node,
#
#     name = String(description='string serialized data')
#     description = String(description='string serialized data')
#     users = List(lambda: User)
#     projects = List(lambda: Project)
#
#
# class Binder(ObjectType):
#     class Meta:
#         interfaces = relay.Node,
#
#     name = String(description="keys in the parameter file")
#     children = List("Binder", description="child binders")
#     files = List(lambda: FileAndDirectory, description="keys in the parameter file")
#     # date_created
#     # date_modified


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
        types = (Directory, File, Parameters, Metrics, TextFile, BinaryFile, JsonFile)


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
