import React, {useState, useEffect} from "react";
import styled from "styled-components";
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import {modernEnvironment} from "../data";
import {by, strOrder} from "../lib/string-sort";
import {fromGlobalId} from "../lib/relay-helpers";
import {ImageView, StyledTitle, TextView, VideoView} from "./FileViews";
import store from "../local-storage";
import {pathJoin} from "../lib/path-join";
import {Box} from "grommet";
import {displayType} from "./file-types";

const {commitMutation} = require("react-relay");

const expQuery = graphql`
  query InlineExperimentViewQuery($id: ID!) {
    experiment (id: $id) {
      id name path
      metrics { id keys }
      directories(first:10000) { edges {node { id name path } } }
      files(first:10000) { edges { node { id name path } } }
    }
  }`;

const dirQuery = graphql`
  query InlineExperimentViewDirectoryQuery($id: ID!) {
    directory (id: $id) {
      id name path
      directories(first:1000) { edges {node { id name path } } }
      files(first:1000) { edges { node { id name path } } }
    }
  }`;
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

function fetchExperiment(inputs) {
  return fetchQuery(modernEnvironment, expQuery, inputs);
}

function fetchDirectory(inputs) {
  return fetchQuery(modernEnvironment, dirQuery, inputs);
}

function InlineFile({id, name}) {
  const {type, id: path} = fromGlobalId(id);
  const src = pathJoin(store.value.profile.url + "/files", path.slice(1));
  console.log(name, displayType(name), src);
  const _ = () => {
    switch (displayType(name)) {
      case "image":
        return <ImageView src={encodeURI(src)}/>;
      case "video":
        return <VideoView src={encodeURI(src)}/>;
      case "ansi":
        return <TextView id={id} key={id} ansi={true}/>;
      case "markdown":
        return <TextView id={id} key={id} ansi={true}/>;
      case "text":
        return <TextView id={id} key={id}/>;
      default:
        return null;
    }
  };
  return <Box>
    <StyledTitle>
      <div className="title" title={name}>{name}</div>
    </StyledTitle>
    {_()}
  </Box>;
}


function InlineMetrics({id, name, keys, addMetricCell, addChart, ..._metrics}) {
  const [selected, setSelection] = useState();
  const {type, id: path} = fromGlobalId(id);
  const src = pathJoin(store.value.profile.url + "/files", path.slice(1));
  return <>
    <Box>
      <StyledTitle>
        <div className="title" title={name}>{name}</div>
      </StyledTitle>
      <StyledContainer>
        {keys.map(k => <StyledItem onClick={() => setSelection(k)}>{k}</StyledItem>)}
      </StyledContainer>
    </Box>
    {selected
        ? <Box>
          <StyledContainer>
            <StyledItem onClick={() => addChart({yKey: selected})}>+ Line Chart</StyledItem>
            <StyledItem onClick={() => addMetricCell({metrics: selected})}>+ Metric Cell</StyledItem>
          </StyledContainer>
        </Box>
        : null}
  </>;
}

function InlineDirView({id, showHidden, onSubmit}) {
  const [{directories, files}, setState] = useState({directories: [], files: []});
  const [queryError, setError] = useState();
  const [selected, select] = useState({id: null});
  const selectedType = selected.id ? fromGlobalId(selected.id).type : null;

  useEffect(() => {
    fetchDirectory({id}).then(({directory, error}) => {
      if (!!error) return setError(error);
      if (!directory) return null;
      let {files, directories} = directory;
      setState({
        directories: directories.edges.map(({node}) => node).sort(by(strOrder, "name")),
        files: files.edges.map(({node}) => node).sort(by(strOrder, "name"))
      })
    });
  }, [id, showHidden]);

  return <>
    <StyledContainer>
      {queryError ? <div>{queryError.toString()}</div> : null}
      {directories.map(f => <Directory active={selected.id === f.id} onClick={() => select(f)} {...f}/>)}
      {files.map(f => <File active={selected.id === f.id} onClick={() => select(f)} {...f}/>)}
    </StyledContainer>
    {selectedType === "Directory" ? <InlineDirView key={selected.id} {...selected}/> : null}
    {selectedType === "File" ? <InlineFile key={selected.id} {...selected}/> : null}
  </>
}

export default function InlineExperimentView({id, showHidden, onSubmit, addMetricCell, addChart}) {
  const [{metrics, directories, files}, setState] = useState({metrics: {}, directories: [], files: []});
  const [queryError, setError] = useState();
  const [selected, select] = useState({id: null});
  const selectedType = selected.id ? fromGlobalId(selected.id).type : null;

  useEffect(() => {
    fetchExperiment({id}).then(({experiment, error}) => {
      if (!!error) return setError(error);
      if (!experiment) return null;
      let {metrics, files, directories} = experiment;
      setState({
        metrics,
        directories: directories.edges.map(({node}) => node).sort(by(strOrder, "name")),
        files: files.edges.map(({node}) => node).sort(by(strOrder, "name"))
      })
    });
  }, [id, showHidden]);

  return <>
    <StyledContainer>
      {queryError ? <div>{queryError.toString()}</div> : null}
      {directories.map(f => <Directory active={selected.id === f.id} onClick={() => select(f)} {...f}/>)}
      {files.map(f => (f.name === "metrics.pkl")
          ? <Metrics name="metrics.pkl" active={selected.id === metrics.id} onClick={() => select(metrics)}/>
          : <File active={selected.id === f.id} onClick={() => select(f)} {...f}/>)}
    </StyledContainer>
    {/*this is a hack, the name for metrics need to be added to the file.*/}
    {selectedType === "Metrics"
        ? <InlineMetrics name="Metrics" addMetricCell={addMetricCell} addChart={addChart} {...metrics}/>
        : null}
    {selectedType === "Directory" ? <InlineDirView key={selected.id} {...selected}/> : null}
    {selectedType === "File" ? <InlineFile key={selected.id} {...selected}/> : null}
  </>;
}

