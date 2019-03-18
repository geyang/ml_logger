import pytest
from graphene.test import Client
from graphql_relay import to_global_id
from ml_dash.schema import schema
from tests import show, shows


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


def test_directory(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery ($id: ID!) {
            directory ( id:  $id ) { 
                id
                name 
                readme {
                    id name path relPath
                    text(stop:11)
                }
                dashConfigs(first:10) {
                    edges {
                        node {
                            id name path relPath
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
                    } }
                }
            }
        }
    """
    path = "/episodeyang/playground/mdp"
    r = client.execute(query, variables=dict(id=to_global_id("Directory", path)))
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
                 "metricsFiles": ["/episodeyang/playground/mdp/experiment_04/metrics.pkl"]}

    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    r = client.execute(query, variables=variables)
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_series(log_dir):
    from ml_dash.config import Args
    Args.logdir = log_dir
    client = Client(schema)
    query = """
        query AppQuery {
            series (
                k:30
                tail: 100
                prefix:"/episodeyang/playground"
                metricsFiles:["experiment_05/metrics.pkl", "experiment_06/metrics.pkl", "experiment_07/metrics.pkl"]
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
                y25
                y75
                y05
                y95
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
            metrics(id:"TWV0cmljczovZXBpc29kZXlhbmcvcGxheWdyb3VuZC9leHBlcmltZW50XzA1L21ldHJpY3MucGts" ) { 
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
