from graphene.test import Client
from ml_dash.schema import schema
from tests import show


def test_directory():
    from ml_dash.config import Args
    Args.logdir = "../../runs"
    client = Client(schema)
    query = """
        query AppQuery ($id: ID!) {
            directory ( id:  $id ) { 
                id
                name 
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
    # r = client.execute(query, variables=dict(id="RGlyZWN0b3J5Oi9lcGlzb2RleWFuZy9wbGF5Z3JvdW5k"))
    r = client.execute(query, variables=dict(id="RGlyZWN0b3J5Oi9lcGlzb2RleWFuZy9wbGF5Z3JvdW5kLw=="))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_series():
    from ml_dash.config import Args
    Args.logdir = "../../runs"
    client = Client(schema)
    query = """
        query AppQuery {
            series (
                prefix:"/episodeyang/playground", 
                xKey: "__timestamp"
                yKey: "sine"
                metricsFiles:["experiment_00/metrics.pkl", "experiment_01/metrics.pkl", "experiment_02/metrics.pkl"]
            ) { 
                id
                xKey
                yKey
                xData
                yData
            }
        }
    """
    r = client.execute(query, variables=dict(username="episodeyang"))
    if 'errors' in r:
        raise RuntimeError(r['errors'])
    else:
        print(">>")
        show(r['data'])


def test_metric():
    from ml_dash.config import Args
    Args.logdir = "../../runs"
    client = Client(schema)
    query = """
        query AppQuery {
            metrics(id:"TWV0cmljczovZXBpc29kZXlhbmcvcGxheWdyb3VuZC9leHBlcmltZW50XzAzL21ldHJpY3MucGts") { 
                id
                keys
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


def test_schema():
    from ml_dash.config import Args
    Args.logdir = "../../runs"
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
