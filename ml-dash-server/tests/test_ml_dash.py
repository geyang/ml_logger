from graphene.test import Client
from ml_dash.schema import schema
from tests import show


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
                        name
                        experiments(first:10){ edges { node { 
                            name
                            parameters {value keys flat raw} 
                            metrics {
                                keys 
                                value (keys: ["__timestamp", "sine"]) 
                            }
                        } } }
                        directories(first:10){
                            edges {
                                node {
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
