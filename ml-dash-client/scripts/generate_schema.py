from graphql.utils import schema_printer
from ml_dash.schema import schema

if __name__ == "__main__":
    with open("../schema.graphql", "w") as f:
        _ = schema_printer.print_schema(schema)
        f.write(_)
