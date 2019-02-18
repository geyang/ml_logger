from graphene import ObjectType, relay, String, List
from ml_dash import schema


class Experiment(ObjectType):
    class Meta:
        interfaces = relay.Node,

    name = String(description="the name for the experiment")
    path = String(description="The root for the experiment")
    # other stuff
    # metricFile: metric.pkl
    # videos: gif, mp4 etc
    # figures: png, jpg
    # files: all files.
    # dashboard: dashboard view
    # charts: chart


def get_experiments(cwd):
    import os
    from ml_dash.config import Args
    return [Experiment(username=_, name="Ge Yang") for _ in os.listdir(Args.logdir)]


def get_experiment(path):
    return Experiment(path=path)
