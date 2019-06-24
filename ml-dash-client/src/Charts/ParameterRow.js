import React, {useEffect, useState} from "react";
import {toGlobalId} from "../lib/relay-helpers";
import {modernEnvironment} from "../data";
import {fetchQuery} from "react-relay";
import {pathJoin} from "../lib/path-join";
import graphql from "babel-plugin-relay/macro";
import JSON5 from "json5";
import Ellipsis from "../components/Ellipsis-2";

function fetchChartConfig(path) {
  let id = toGlobalId("File", path);
  return fetchQuery(modernEnvironment, graphql`
      query ParameterRowChartConfigQuery($id: ID!) {
          node (id: $id) { id ...on File { yaml } }
      }`, {id});
}

function fetchParameters(path) {
  let id = toGlobalId("Parameters", path);
  return fetchQuery(modernEnvironment, graphql`
      query ParameterRowQuery($id: ID!) {
          node (id: $id) { id ...on Parameters { flat } }
      }`, {id});
}

export default function ParameterRow({path, paramKeys}) {
  const [flatParams, setParameters] = useState({});
  const [keys, setKeys] = useState(paramKeys || []);
  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    fetchParameters(pathJoin(path, "parameters.pkl")).then(({node, errors}) => {
      if (!!errors || !node) return null;
      if (running) setParameters(node.flat);
    });
    return abort;
  }, [path, setParameters]);
  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    if (!paramKeys || !paramKeys.length)
      fetchChartConfig(pathJoin(path, ".charts.yml")).then(({node, errors}) => {
        if (!!errors || !node || !node.yaml || typeof node.yaml.keys === 'function') return null;
        if (running) setKeys(node.yaml.keys || []);
      });
    else setKeys(paramKeys);
    return abort;
  }, [path, paramKeys, setKeys]);
  if (keys && keys.length)
    return <>{
      keys.map(k => {
            if (typeof k === 'string') {
              const head = k.split('.');
              const last = head.pop();
              return <div className="item" key={k}>
                {head ? <div className="root">{head.join('.') + '.'}</div> : null}
                <span>{last}:</span>
                {flatParams
                    ? <Ellipsis className="badge">{JSON5.stringify(flatParams[k])}</Ellipsis>
                    : "-"
                }</div>
            } else {
              return <div className="item" key={k.metrics}>
                <div className="root">metrics.</div>
                <span className="key">{k.metrics}:</span>
                <span className="value">N/A</span>
              </div>
            }
          }
      )}</>;
  return null;
}
