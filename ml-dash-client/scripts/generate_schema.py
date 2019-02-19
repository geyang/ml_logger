import os
from graphql.utils import schema_printer
from ml_dash.schema import schema

if __name__ == "__main__":
    target_path = os.path.join(os.path.dirname(__file__), "../schema.graphql")
    with open(target_path, "w") as f:
        _ = schema_printer.print_schema(schema)
        f.write(_)
