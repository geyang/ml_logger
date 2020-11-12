import pytest
from graphene.test import Client
from graphql_relay import to_global_id
from ml_dash.schema import schema
from dash_server_specs import show, shows


@pytest.fixture(scope='session')
def log_dir(request):
    return request.config.getoption('--log-dir')


def test_delete_text_file(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        mutation AppMutation ($id: ID!) {
            deleteFile (input: { 
                            id: $id, 
                            clientMutationId: "10", 
             }) { ok }
        }
    """
    path = "/episodeyang/cpc-belief/README.md"
    r = client.execute(query, variables=dict(id=to_global_id("File", path)))

    if 'errors' in r:
        raise RuntimeError("\n" + shows(r['errors']))
    else:
        print(">>")
        show(r['data'])


def test_mutate_text_file(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        mutation AppMutation ($id: ID!) {
            updateText (input: { 
                            id: $id, 
                            text: "new text!!\\n1\\n2\\n3\\n4\\n5\\n6",
                            clientMutationId: "10", 
             }) { 
                file { id name text (stop:5) }
            }
        }
    """
    path = "/episodeyang/cpc-belief/README.md"
    r = client.execute(query, variables=dict(id=to_global_id("File", path)))

    if 'errors' in r:
        raise RuntimeError("\n" + shows(r['errors']))
    else:
        print(">>")
        show(r['data'])


def test_mutate_json_file(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        mutation AppMutation ($id: ID!) {
            updateJson (input: { 
                            id: $id, 
                            data: {text: "hey", key: 10},
                            clientMutationId: "10", 
             }) { 
                file { id name json text yaml }
            }
        }
    """
    path = "/episodeyang/cpc-belief/README.md"
    r = client.execute(query, variables=dict(id=to_global_id("File", path)))

    if 'errors' in r:
        raise RuntimeError("\n" + shows(r['errors']))
    else:
        print(">>")
        show(r['data'])


def test_mutate_yaml_file(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        mutation AppMutation ($id: ID!) {
            updateYaml (input: { 
                            id: $id, 
                            data: {text: "hey", key: 10, charts: [0, 1]},
                            clientMutationId: "10", 
             }) { 
                file { id name text yaml }
            }
        }
    """
    path = "/episodeyang/cpc-belief/README.md"
    r = client.execute(query, variables=dict(id=to_global_id("File", path)))

    if 'errors' in r:
        raise RuntimeError("\n" + shows(r['errors']))
    else:
        print(">>")
        show(r['data'])


def test_glob_files(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery ($cwd: String!, $query: String) {
            glob ( cwd: $cwd, query: $query) { id name path }
        }
    """
    path = "/episodeyang/cpc-belief/mdp/experiment_00/"
    r = client.execute(query, variables=dict(cwd=path, query="figures/*.png"))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_experiment(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery ($id: ID!) {
            experiment ( id:  $id ) { 
                id
                name 
                parameters { id name }
                files (first:10) {
                    edges {
                        node {
                            id name path
                        }
                    }
                }
                directories (first:10) {
                    edges {
                        node {
                            id name path
                        }
                    }
                }
            }
        }
    """
    path = "/episodeyang/cpc-belief/mdp/experiment_01"
    r = client.execute(query, variables=dict(id=to_global_id("Experiment", path)))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_directory(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery ($id: ID!) {
            directory ( id:  $id ) { 
                id
                name 
                path
                readme {
                    id name path 
                    text(stop:11)
                }
                dashConfigs(first:10) {
                    edges {
                        node {
                            id name 
                            path 
                            yaml
                            text(stop:11)
                        }
                    }
                }
                
                charts(first:10) {
                    edges {
                        node {
                            id name 
                            dir 
                            path 
                            yaml
                            text(stop:11)
                        }
                    }
                }
                
                directories (first:10) {
                    edges {
                        node {
                            id name path
                            directories (first:10) {
                                edges {
                                    node {
                                        id name
                                    }
                                }
                            }
                        }
                    }
                }
                experiments (first:10) {
                    edges { node { 
                        id name path
                        parameters {keys flat}
                        files (first:10) { edges { node { id, name} } }
                    } }
                }
            }
        }
    """
    path = "/episodeyang/cpc-belief/mdp"
    r = client.execute(query, variables=dict(id=to_global_id("Directory", path)))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


# todo: add chunked loading for the text field. Necessary for long log files.
def test_reac_text_file(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery ($id: ID!) {
            file ( id:  $id) { 
                id name text
            }
        }
    """
    path = "/episodeyang/cpc-belief/README.md"
    r = client.execute(query, variables=dict(id=to_global_id("File", path)))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_series_2(log_dir):
    query = """
    query LineChartsQuery(
      $prefix: String
      $xKey: String
      $yKey: String
      $yKeys: [String]
      $metricsFiles: [String]!
    ) {
      series(metricsFiles: $metricsFiles, prefix: $prefix, k: 10, xKey: $xKey, yKey: $yKey, yKeys: $yKeys) {
        id
        xKey
        yKey
        xData
        yMean
        yCount
      }
    }
    """
    variables = {"prefix": None, "xKey": "epoch", "yKey": "slow_sine", "yKeys": None,
                 "metricsFiles": ["/episodeyang/cpc-belief/mdp/experiment_01/metrics.pkl"]}

    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    r = client.execute(query, variables=variables)
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])

    assert r['data']['series']['xData'].__len__() == 10


def test_series_x_limit(log_dir):
    query = """
    query LineChartsQuery(
      $prefix: String
      $xKey: String
      $yKey: String
      $yKeys: [String]
      $metricsFiles: [String]!
    ) {
      series(
        metricsFiles: $metricsFiles, 
        prefix: $prefix, 
        k: 10, 
        xLow: 100,
        xKey: $xKey, 
        yKey: $yKey, 
        yKeys: $yKeys
        ) {
            id
            xKey
            yKey
            xData
            yMean
            yCount
          }
    }
    """

    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)

    variables = {"prefix": None, "xKey": "epoch", "yKey": "slow_sine", "yKeys": None,
                 "metricsFiles": ["/episodeyang/cpc-belief/mdp/experiment_01/metrics.pkl"]}
    r = client.execute(query, variables=variables)
    print(r['data']['series']['xData'])
    assert r['data']['series']['xData'].__len__() == 10

    variables = {"prefix": None, "yKey": "slow_sine", "yKeys": None,
                 "metricsFiles": ["/episodeyang/cpc-belief/mdp/experiment_01/metrics.pkl"]}
    r = client.execute(query, variables=variables)
    print(r['data']['series']['xData'])
    assert r['data']['series']['xData'].__len__() == 10


def test_series_last(log_dir):
    query = """
    query LastMetricQuery(
      $yKey: String
      $last: Int
      $metricsFiles: [String]!
    ) {
      series(metricsFiles: $metricsFiles, k: 1, yKey: $yKey, tail: $last) {
        id
        yKey
        yMean
        yCount
      }
    }
    """
    variables = {"yKey": "slow_sine",
                 "last": 100,
                 "metricsFiles": ["/episodeyang/cpc-belief/mdp/experiment_01/metrics.pkl"]}

    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    r = client.execute(query, variables=variables)
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])
        assert not not r['data']['series']['yMean'], "the yMean should NOT be empty"
        assert not not r['data']['series']['yCount'] == [100.0]


# can we do the average first?
def test_series_group(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery {
            series (
                k:30
                tail: 100
                xLow: 25
                prefix:"/episodeyang/cpc-belief/mdp"
                metricsFiles:["experiment_00/metrics.pkl", "experiment_01/metrics.pkl", "experiment_02/metrics.pkl"]
                # xKey: "__timestamp"
                xKey: "epoch"
                # yKey: "sine"
                yKeys: ["sine", "slow_sine"]
                # xAlign: "start"
            ) { 
                id
                xKey
                yKey
                yKeys
                xData
                yMean
                yMedian
                y25pc
                y75pc
                y05pc
                y95pc
                yMedian
                yCount
            }
        }
    """
    r = client.execute(query, variables=dict(username="episodeyang"))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_metric(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery {
            metrics(id:"TWV0cmljczovZXBpc29kZXlhbmcvY3BjLWJlbGllZi9tZHAvZXhwZXJpbWVudF8wMC9tZXRyaWNzLnBrbA==" ) { 
                id
                keys
                path
                value (keys: ["__timestamp", "sine"])
            }
        }
    """
    r = client.execute(query, variables=dict(username="episodeyang"))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_schema(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery ($username:String) {
            user (username: $username) {
                username 
                name 
                projects(first: 1) {
                  edges {
                    node {
                        id
                        name
                        experiments(first:10) { edges { node { 
                            id
                            name
                            parameters {value keys flat raw} 
                            metrics {
                                id
                                keys 
                                value (keys: ["__timestamp", "sine"]) 
                            }
                        } } }
                        directories(first:10){
                            edges {
                                node {
                                    id
                                    name
                                    files(first:10){
                                        edges {
                                            node { name }
                                        }
                                    }
                                    directories(first:10){
                                        edges {
                                            node { name }
                                        }
                                    }
                                }
                            }
                        }
                    }
                  }
                }
            }
        }
    """
    r = client.execute(query, variables=dict(username="episodeyang"))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        _ = r['data']['user']
        show(_)


def test_node(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery ($id:ID!) {
            node (id: $id) {
                id
                ... on File {
                    name
                    text
                }
            }
        }
    """
    path = "/episodeyang/cpc-belief/README.md"
    r = client.execute(query, variables=dict(id=to_global_id("File", path)))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])
