from os.path import join, isabs

import numpy as np
import pandas as pd
from graphene import relay, ObjectType, String, List, ID, Int, Float
from graphene.types.generic import GenericScalar
from ml_dash.config import Args
from ml_dash.schema.files.file_helpers import read_dataframe


def get_column(df, key, stat_key):
    try:
        return df[key][stat_key].to_numpy().tolist()
    except:
        return []


def get_columns(df, keys, stat_key):
    return {k: get_column(df, k, stat_key) for k in keys}


class Series(ObjectType):
    class Meta:
        interfaces = relay.Node,

    path = String(description="the file path for the configuration file")

    prefix = String(description='path prefix for the metrics files')
    metrics_files = List(ID, description="List of metrics file IDs that we use to aggregate this series")

    _df = GenericScalar(description='the processed dataframe object that aggregates all metrics files.')

    window = Float(description="the window for the rolling average")

    label = String(description="the lable for the series")
    x_key = String(description="key for the x")
    y_key = String(description="key for the y axis")
    y_keys = List(String, description="list of keys for the y axis")

    # stype = SeriesTyes(description="the type of series data")

    # resolved from dataset
    x_data = GenericScalar(description="x data")
    y_mean = GenericScalar(description="y data from the mean of the window")
    # y_mode = GenericScalar(description="y data as from mode of the window")
    y_median = GenericScalar(description="y data as from mode of the window")
    y_min = GenericScalar(description="min in each bin")
    y_max = GenericScalar(description="max in each bin")
    y_25pc = GenericScalar(description="quarter quantile")
    y_75pc = GenericScalar(description="3/4th quantile")
    y_95pc = GenericScalar(description="95th quantile")
    y_05pc = GenericScalar(description="5th quantile")
    # Note: confidence level only applies to mean. So only group has it.
    # y_c95 = GenericScalar(description="95th confidence")
    y_count = GenericScalar(description="the number of datapoints used to compute each tick")

    warning = String(description="Warning Message")

    # todo: start time

    # todo: need to move the keys out, so that we can dropnan on the joint table.
    #   Otherwise the different data columns would not necessarily be the same length.
    def resolve_x_data(self, info):
        # note: new in 0.24.1.
        #  ~> df.value.dtype does NOT work for categorical data.
        _ = self._df['__x'].to_numpy()
        if np.issubdtype(_.dtype, np.datetime64):
            return (_.astype(int) / 1000).tolist()
        elif np.issubdtype(_.dtype, np.timedelta64):
            return (_.astype(int) / 1000).tolist()
        return _.tolist()

    def resolve_y_mean(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, 'mean')
        return get_columns(self._df, self.y_keys, 'mean')

    # def resolve_y_mode(self, info):
    #     if self.y_key is not None:
    #         return self._df[self.y_key]['mode'].to_numpy().tolist()
    #     return {k: self._df[k]['mode'].to_numpy().tolist() for k in self.y_keys}

    def resolve_y_min(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, 'min')
        return get_columns(self._df, self.y_keys, 'min')

    def resolve_y_max(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, 'max')
        return get_columns(self._df, self.y_keys, 'max')

    def resolve_y_median(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, '50%')
        return get_columns(self._df, self.y_keys, '50%')

    def resolve_y_25pc(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, '25%')
        return get_columns(self._df, self.y_keys, '25%')

    def resolve_y_75pc(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, '75%')
        return get_columns(self._df, self.y_keys, '75%')

    def resolve_y_95pc(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, '95%')
        return get_columns(self._df, self.y_keys, '95%')

    def resolve_y_05pc(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, '5%')
        return get_columns(self._df, self.y_keys, '5%')

    def resolve_y_count(self, info):
        if self.y_key is not None:
            return get_column(self._df, self.y_key, 'count')
        return get_columns(self._df, self.y_keys, 'count')

    @classmethod
    def get_node(cls, info, id):
        return Series(id)


def get_series(metrics_files=tuple(),
               prefix=None,
               head=None,
               tail=None,
               x_low=None,
               x_high=None,
               x_edge=None,  # OneOf('start', 'after', 'mid', 'mode')
               k=None,
               x_align=None,  # OneOf(int, 'left', 'right')
               x_key=None,
               y_key=None,
               y_keys=None,
               label=None):
    warning = None
    assert not y_key or not y_keys, "yKey and yKeys can not be trueful at the same time"
    assert y_key or y_keys, "yKey and yKeys can not be both falseful."
    assert head is None or tail is None, "head and tail can not be trueful at the same time"
    if not prefix:
        for id in metrics_files:
            assert isabs(id), f"metricFile need to be absolute path is prefix is {prefix}. It is {id} instead."

    ids = [join(prefix or "", id) for id in metrics_files]
    dfs = [read_dataframe(join(Args.logdir, _id[1:])) for _id in ids]

    y_keys = y_keys or [y_key]
    join_keys = [k for k in {x_key, *y_keys} if k is not None]

    dataframes = []
    for df in dfs:
        if df is None:
            df['index'] = df.index
            df.set_index('index')
            continue
        elif x_key is not None:
            df.set_index(x_key)
            if x_align is None:
                pass
            elif x_align == "start":  # todo: this needs to be part of the join
                df[x_key] -= df[x_key][0]
            elif x_align == "end":
                df[x_key] -= df[x_key][-1]
            else:
                df[x_key] -= x_align
        else:
            df = df[y_keys]
            df['index'] = df.index
            df.set_index('index')

        # todo: maybe apply tail and head *after* dropna??
        if tail is not None:
            df = df.tail(tail)
        if head is not None:
            df = df.head(head)
        inds = True
        if x_low is not None:
            inds &= df[x_key or "index"] >= x_low
            print("x_low >>>", inds)
        if x_high is not None:
            inds &= df[x_key or "index"] <= x_high
            print("x_high >>>", inds)
        if inds is not True:
            df = df.loc[inds]

        # todo: only dropna if we are not using ranges. <need to test>
        try:
            column = df[join_keys]
            if head is None and tail is None:
                dataframes.append(column.dropna())
            else:
                dataframes.append(column)
        except KeyError as e:
            raise KeyError(f"{join_keys} contain keys that is not in the dataframe. "
                           f"Keys available include {df.keys()}") from e

    if not dataframes:  # No dataframe, return `null`.
        return None

    all = pd.concat(dataframes)

    if x_key:
        all = all.set_index(x_key)

    all.rank(method='first')

    if k is not None:
        bins = pd.qcut(all.index, k, duplicates='drop')
        grouped = all.groupby(bins)
        # df
    else:
        grouped = all.groupby(level=0)

    # treat all numbers in bin as equal. For raw (not averaged, or averaged)
    grouped[y_keys].agg(['count', 'mean', 'min', 'max'])
    df = grouped[y_keys].describe(percentiles=[0.25, 0.75, 0.5, 0.05, 0.95]).reset_index()

    if k is not None:
        if 'index' not in df:
            df['index'] = df.index
        if x_edge == "right" or x_edge is None:
            df['__x'] = df['index'].apply(lambda r: r.right)
        elif x_edge == "left":
            df['__x'] = df['index'].apply(lambda r: r.left)
        elif x_edge == "mean":
            df['__x'] = df['index'].apply(lambda r: 0.5 * (r.left + r.right))
        # todo: use mode of each bin
        else:
            raise KeyError(f"x_edge {[x_edge]} should be OneOf['start', 'after', 'mid', 'mode']")
    else:
        df['__x'] = df.index

    return Series(metrics_files,
                  _df=df.sort_values(by="__x"),
                  metrics_files=metrics_files,
                  prefix=prefix,
                  x_key=x_key or "index",
                  y_key=y_key,
                  y_keys=y_keys,
                  label=label,
                  warning=warning)


SeriesArguments = dict(
    metrics_files=List(String, required=True),
    prefix=String(description="prefix to the metricFiles.", required=False),
    head=Int(description="the number of datapoints (for each metrics file) to take from the head-end"),
    tail=Int(description="the number of datapoints (for each metrics file) to take from the tail-end"),
    x_low=Float(description="the (inclusive) lower end of the x column"),
    x_high=Float(description="the (inclusive) higher end of the x column"),
    k=Int(required=False, description='the number of datapoints to return.'),
    x_align=String(description="a number (anchor point), 'start', 'end'"),
    x_key=String(),
    y_key=String(description="You can leave the xKey, but the yKey is required."),
    y_keys=List(String, description="Alternatively you can pass a list of keys to yKey*s*."),
    label=String(),
    warning=String(),
)

# if __name__ == "__main__":
