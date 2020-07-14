import base64
from cloudpickle import cloudpickle

# todo: cloudpickle, just like regular pickle, require the availability
#  of the relevant python modules for the hydrated python object. For
#  this reason, it is a poor choice for serializing pkl objects that
#  just need to be dumped.

def deserialize(code):
    data = cloudpickle.loads(base64.b64decode(code))
    return data


def serialize(data):
    code = cloudpickle.dumps(data)
    return base64.b64encode(code).decode("utf-8")
