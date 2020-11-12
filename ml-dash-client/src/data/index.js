import {Environment, Network, QueryResponseCache, RecordSource, Store} from 'relay-runtime';
import JSON5 from 'json5';
import store from "../local-storage";
import {pathJoin} from "../lib/path-join";

export let tempID = 0;
export const inc = () => tempID++;

const oneMinute = 60 * 1000;
const cache = new QueryResponseCache({size: 250, ttl: oneMinute});

function fetchQuery(
    operation,
    variables,
    cacheConfig,
) {
  const queryID = operation.text;
  const isMutation = operation.operationKind === 'mutation';
  const isQuery = operation.operationKind === 'query';

  // note: Try to get data from cache on queries
  const forceFetch = cacheConfig && cacheConfig.force;
  // const fromCache = cache.get(queryID, variables);
  // if (isQuery && fromCache !== null && !forceFetch)
  //   return fromCache;

  // note: Otherwise, fetch data from server
  const controller = new AbortController();
  // promise.abort = () => controller.abort();
  return fetch(
      pathJoin(store.value.profile.url, "/graphql"),
      {
        signal: controller.signal,
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({
          query: operation.text,
          variables,
        }),
      })
      .then(response => response.text())
      .then(text => JSON5.parse(text))
      .then(json => {
        // Update cache on queries
        if (isQuery && json) {
          cache.set(queryID, variables, json);
        }
        // Clear cache on mutations
        if (isMutation) {
          cache.clear();
        }

        return json;
      });
}

export const modernEnvironment = new Environment({
  network: Network.create(fetchQuery),
  store: new Store(new RecordSource()),
});

