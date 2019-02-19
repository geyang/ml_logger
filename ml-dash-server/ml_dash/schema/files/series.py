from os.path import split, realpath, join

import numpy as np
from graphene import relay, ObjectType, String, List, JSONString, ID, Enum, Date, Time, DateTime, Int, Float, Union
from graphene.types.generic import GenericScalar
from ml_dash import schema
from ml_dash.config import Args
from ml_dash.schema.files.file_helpers import find_files, read_records, read_dataframe


# class SeriesTyes(Enum):
#     key = None,
#     mean = "mean",
#     min_max = "mean", "min", "max"
#     mode = "mode",
#     mean_stddev = "mean", 'stddev'
#     mode_stddev = "mode", "stddev"
#     stddev = "mean", "mode", "stddev"
#     quantile = "mean", "25", "75", "0", "100"

# class DataType(Union):
#     class Meta:
#         types = Int, Float, Date, Time, DateTime


class Series(ObjectType):
    class Meta:
        interfaces = relay.Node,

    path = String(description="the file path for the configuration file")

    prefix = String(description='path prefix for the metrics files')
    metrics_files = List(ID, description="List of metrics file IDs that we use to aggregate this series")

    _df = GenericScalar(description='the dataframe object')
    _dfs = GenericScalar(description='a list of the dataframe objects')

    window = Float(description="the window for the rolling average")

    label = String(description="the lable for the series")
    x_key = String(description="key for the x")
    y_key = String(description="key for the y axis")
    y_keys = List(String, description="tuple of keys for the y axis")

    # stype = SeriesTyes(description="the type of series data")

    # resolved from dataset
    x_data = List(GenericScalar, description="x data")
    y_data = List(GenericScalar, description="y data, usually mode or mean")
    y_25 = List(GenericScalar, description="quarter quantile")
    y_75 = List(GenericScalar, description="3/4th quantile")
    y_0 = List(GenericScalar, description="0% quantile")
    y_100 = List(GenericScalar, description="100% quantile")
    y_stddev = List(GenericScalar, description="standard deviation")

    # todo: need to move the keys out, so that we can dropnan on the joint table.
    #   Otherwise the different data columns would not necessarily be the same length.
    def resolve_x_data(self, info):
        # todo: error handling on KeyError
        s = self._df[self.x_key]
        return self._df[self.x_key].values.tolist()

    def resolve_y_data(self, info):
        return self._df[self.y_key].values.tolist()

    def resolve_y_25(self, info):
        # todo: error handling on KeyError
        return self._df[self.y_key + "/25"].values.tolist()

    def resolve_y_75(self, info):
        # todo: error handling on KeyError
        return self._df[self.y_key + "/75"].values.tolist()

    def resolve_y_0(self, info):
        # todo: error handling on KeyError
        return self._df[self.y_key + "/0"].values.tolist()

    def resolve_y_100(self, info):
        # todo: error handling on KeyError
        return self._df[self.y_key + "/100"].values.tolist()

    def resolve_y_stddev(self, info):
        return self._df[self.y_key + "/stddev"].values.tolist()

    @classmethod
    def get_node(cls, info, id):
        return Series(id)


def get_series(metrics_files=tuple(), prefix=None, window=None, x_key=None, y_key=None, label=None):
    ids = [join(prefix or "", id) for id in metrics_files]
    dfs = [read_dataframe(join(Args.logdir, _id[1:])) for _id in ids]
    return Series(metrics_files, prefix=prefix, _df=dfs[0], window=window, x_key=x_key, y_key=y_key, label=label, )
