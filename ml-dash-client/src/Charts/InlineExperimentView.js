import React, {useState, useEffect} from "react";
import styled from "styled-components";
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import {modernEnvironment} from "../data";
import {by, strOrder} from "../lib/string-sort";
import {fromGlobalId, toGlobalId} from "../lib/relay-helpers";
import {ImageView, StyledTitle, TextView, VideoView} from "./FileViews";
import store from "../local-storage";
import {pathJoin} from "../lib/path-join";
import {Box} from "grommet";
import {displayType} from "./file-types";
import Ellipsis from "../components/Form/Ellipsis";

const {commitMutation} = require("react-relay");

//todo: change to node() {... on Experimen}
const StyledContainer = styled.div`
  padding: 10px;
  overflow-y: auto;
  white-space: normal;
`;
const StyledItem = styled.div`
  display: inline-block;
  cursor: pointer;
  margin: 2px;
  padding: 0 7px;
  line-height: 2em;
  border-radius: 14px;
  ${({active}) => active && "background: #e6e6e6"}
  &:hover {
    color: white;
    background: #23aaff;
  }
`;


function Metrics({name, ..._}) {
  return <StyledItem {..._}>{name}</StyledItem>
}

function Directory({name, ..._}) {
  return <StyledItem {..._}>{name}</StyledItem>
}

function File({name, ..._}) {
  return <StyledItem {..._}>{name}</StyledItem>
}

function fetchExperiment(path) {
  let id = toGlobalId("Experiment", path);
  return fetchQuery(modernEnvironment, graphql`
      query InlineExperimentViewQuery($id: ID!) {
          experiment (id: $id) {
              id name path
              metrics { name path keys }
              directories(first:100) { edges {node { name path } } }
              files(first:100) { edges { node { name path } } }
          }
      }`, {id});
}

function fetchDirectory(path) {
  let id = toGlobalId("Directory", path);
  return fetchQuery(modernEnvironment, graphql`
      query InlineExperimentViewDirectoryQuery($id: ID!) {
          directory (id: $id) {
              id name path
              directories(first:100) { edges {node { name path } } }
              files(first:100) { edges { node { name path } } }
          }
      }`, {id});
}

function InlineFile({path, name}) {
  const src = pathJoin(store.value.profile.url, "files", path.slice(1));
  console.log(displayType(name, src));
  const _ = () => {
    switch (displayType(name)) {
      case "image":
        return <ImageView src={encodeURI(src)}/>;
      case "video":
        return <VideoView src={encodeURI(src)}/>;
      case "ansi":
        return <TextView path={path} key={path} ansi={true}/>;
      case "markdown":
        return <TextView path={path} key={path} ansi={true}/>;
      case "text":
        return <TextView path={path} key={path}/>;
      default:
        // return null;
        // note: if no type is detected, show as text file.
        return <TextView path={path} key={path}/>;
    }
  };
  return <Box>
    <StyledTitle>
      <Ellipsis className="title" title={name || "N/A"}
                text={name || "N/A"}
                padding="2em"/>
    </StyledTitle>
    {_()}
  </Box>;
}


function InlineMetrics({path, name, keys, addMetricCell, addChart, ..._metrics}) {
  const id = toGlobalId("Metrics", path);
  const [selectedKey, select] = useState();
  //todo: for downloading the file
  // const src = pathJoin(store.value.profile.url + "/files", path.slice(1));
  return <>
    <Box>
      <StyledTitle>
        <Ellipsis className="title" title={name || "N/A"}
                  text={name || "N/A"}
                  padding="2em"/>
      </StyledTitle>
      <StyledContainer>
        {keys.map(k => <StyledItem key={k} onClick={() => select(k)}>{k}</StyledItem>)}
      </StyledContainer>
    </Box>
    {selectedKey
        ? <Box>
          <StyledContainer>
            <StyledItem onClick={() => addChart({yKey: selectedKey})}>+ Line Chart</StyledItem>
            <StyledItem onClick={() => addMetricCell({metrics: selectedKey})}>+ Metric Cell</StyledItem>
          </StyledContainer>
        </Box>
        : null}
  </>;
}

function InlineDirView({path, showHidden, onSubmit}) {
  const [{directories, files}, setState] = useState({directories: [], files: []});
  const [queryError, setError] = useState();
  const [selected, select] = useState({});

  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    fetchDirectory(path).then(({directory, error}) => {
      if (!!error) return setError(error);
      if (!directory) return null;
      let {files, directories} = directory;
      if (running)
        setState({
          directories: directories.edges.map(({node}) => node).sort(by(strOrder, "name")),
          files: files.edges.map(({node}) => node).sort(by(strOrder, "name"))
        });
    });
    return abort;
  }, [path, showHidden]);

  return <>
    <StyledContainer>
      {queryError ? <div>{queryError.toString()}</div> : null}
      {directories.map(f => <Directory key={f.name} active={selected.path === f.path} {...f}
                                       onClick={() => select({type: "Directory", ...f})}/>)}
      {files.map(f => <File key={f.name} active={selected.path === f.path} {...f}
                            onClick={() => select({type: "File", ...f})}/>)}
    </StyledContainer>
    {selected.type === "Directory" ? <InlineDirView key={selected.path} {...selected}/> : null}
    {selected.type === "File" ? <InlineFile key={selected.path} {...selected}/> : null}
  </>
}

export default function InlineExperimentView({path, showHidden, onSubmit, addMetricCell, addChart}) {
  const [{metrics, directories, files}, setState] = useState({metrics: {}, directories: [], files: []});
  const [queryError, setError] = useState();
  const [selected, select] = useState({});
  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    fetchExperiment(path).then(({experiment, error}) => {
      if (!!error) return setError(error);
      if (!experiment) return null;
      let {metrics, files, directories} = experiment;
      if (running)
        setState({
          metrics,
          directories: directories.edges.map(({node}) => node).sort(by(strOrder, "name")),
          files: files.edges.map(({node}) => node).sort(by(strOrder, "name"))
        });
    });
    return abort;
  }, [path, showHidden]);

  return <>
    <StyledContainer>
      {queryError ? <div>{queryError.toString()}</div> : null}
      {directories.map(f => <Directory key={f.name} active={selected.path === f.path}
                                       onClick={() => select({type: "Directory", ...f})} {...f}/>)}
      {files.map(f => (f.name === "metrics.pkl")
          ? <Metrics key={f.name}
                     name="metrics.pkl" active={selected === metrics.id}
                     onClick={() => select({type: "Metrics", ...f})}/>
          : <File key={f.name} active={selected.path === f.path}
                  onClick={() => select({type: "File", ...f})} {...f}/>)}
    </StyledContainer>
    {selected.type === "Metrics" //hack: the name for metrics need to be added to the file.
        ? <InlineMetrics name="Metrics" addMetricCell={addMetricCell} addChart={addChart} {...metrics}/>
        : null}
    {selected.type === "Directory" ? <InlineDirView key={selected} {...selected}/> : null}
    {selected.type === "File" ? <InlineFile key={selected} {...selected}/> : null}
  </>;
}

