import {Environment, Network, RecordSource, Store} from 'relay-runtime';
import JSON5 from 'json5';

function fetchQuery(operation, variables) {
  return fetch('http://localhost:8081/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({query: operation.text, variables,}),
  })
      .then(response => response.text())
      .then(text => JSON5.parse(text));
}

export const modernEnvironment = new Environment({
  network: Network.create(fetchQuery),
  store: new Store(new RecordSource()),
});
