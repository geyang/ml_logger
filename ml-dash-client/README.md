# Dev Notes

To start the graphql server:

```bash
cd ml-dash-server
make start
```

This should start a visualization backend server on the port 8081.

To start the client with dev server run

```bash
cd ml-dash-client
yarn start
```

This should start a dev server serving the client at port 3001. GraphQueries are pointed to 8081.

### Generating Sample Experiments

run [../ml-dash-server/tests/ create_experiments.py](../server/tests/create_experiments.py), which 
would generate experiment records inside a `./runs` folder.
