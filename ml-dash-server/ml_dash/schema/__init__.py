from graphene import relay, ObjectType, Float, Schema, AbstractType, List, String, Union, Field
from ml_dash.schema.experiments import Experiment
from ml_dash.schema.schema_helpers import bind, bind_args
from ml_dash.schema.users import User, get_users, get_user
from ml_dash.schema.projects import Project
from ml_dash.schema.directories import Directory
from ml_dash.schema.files import File

from ml_dash.data import create_ship, get_faction, get_ship


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

    ship = relay.Node.Field(Ship)
    faction = relay.Node.Field(Faction)

    @classmethod
    def mutate_and_get_payload(
            cls, root, info, ship_name, faction_id, client_mutation_id=None
    ):
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=ship, faction=faction)


class Query(ObjectType):
    node = relay.Node.Field()
    # context?
    # todo: files
    # todo: series

    users = Field(List(User), resolver=bind_args(get_users))
    user = Field(User, username=String(), resolver=bind_args(get_user))

    # Not Implemented atm
    # teams = relay.Node.Field(List(Team))
    # team = relay.Node.Field(Team)

    projects = relay.Node.Field(List(Project))
    project = relay.Node.Field(Project)

    # dirs
    # files

    # Not Implemented atm
    # experiments = relay.Node.Field(List(Experiment))
    # experiment = relay.Node.Field(Experiment)

    # def resolve_user(self, username):
    #     return get_user(username)
    #
    # def resolve_users(self, team=None):
    #     return get_users(team=team)

    # rebels = relay.Node.Field(Faction)
    # empire = relay.Node.Field(Faction)
    # node = relay.Node.Field()
    #
    # def resolve_rebels(self, info):
    #     return get_rebels()
    #
    # def resolve_empire(self, info):
    #     return get_empire()


class Mutation(ObjectType):
    # todo: remove_file
    # todo: rename_file
    # todo: edit_file
    # todo: move_file
    # todo: copy_file

    introduce_ship = IntroduceShip.Field()


schema = Schema(query=Query, mutation=Mutation)
