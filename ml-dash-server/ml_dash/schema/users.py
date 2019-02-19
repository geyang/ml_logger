from os.path import isfile
from graphene import ObjectType, relay, String
from ml_dash import schema


class User(ObjectType):
    class Meta:
        interfaces = relay.Node,

    @classmethod
    def get_node(_, info, id):
        print(info, id)
        return get_user(id)

    username = String(description='string serialized data')
    name = String(description='string serialized data')

    projects = relay.ConnectionField(lambda: schema.projects.ProjectConnection)

    def resolve_projects(self, info, **kwargs):
        return schema.projects.get_projects(self.username)

    # teams = List(lambda: schema.Team)


def get_users(ids=None):
    import os
    from ml_dash.config import Args
    return [User(username=_, name="Ge Yang") for _ in os.listdir(Args.logdir) if not isfile(_)]


def get_user(username):
    return User(username=username, name="Ge Yang", id=username)
