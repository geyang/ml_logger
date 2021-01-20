import React, {useState, useEffect} from "react";
import {useToggle} from "react-use";
import styled from "styled-components";
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import {Box, Image, Video, RangeInput} from "grommet";
import Ansi from "ansi-to-react";

import {modernEnvironment, inc} from "../data";
import {by, commonPrefix, strOrder, subPrefix} from "../lib/string-sort";
import {pathJoin} from "../lib/path-join";
import store from "../local-storage";
import LineChart from "./LineChart";
import {commitMutation} from "react-relay";
import MonacoEditor from "react-monaco-editor";
import {toGlobalId} from "../lib/relay-helpers";
import Ellipsis from "../components/Form/Ellipsis";
import {RowContainer} from "../components/layouts";
import JSON5 from "json5";
import CompoundChart, {numOfFacets, numOfLines} from "./CompoundChart";
import {RefreshCw, X} from "react-feather";

const globQuery = graphql`
    query FileViewsQuery ($cwd: String!, $glob: String) {
        glob ( cwd: $cwd, query: $glob) {
            id name path
        }
    }
`;


function globFiles({cwd, glob}) {
  return fetchQuery(modernEnvironment, globQuery, {cwd, glob});
}

export function fetchTextFile(path) {
  let id = toGlobalId("File", path);
  return fetchQuery(modernEnvironment, graphql`
      query FileViewsTextFileQuery ($id: ID!) {
          node (id: $id) {
              id
              ... on File { text }
          }
      }`, {id})
}

export function fetchAllCharts(path) {
  let id = toGlobalId("Directory", path);
  return fetchQuery(modernEnvironment, graphql`
      query FileViewsChartsQuery ($id: ID!) {
          node (id: $id) {
              id
              ... on Directory  {
                  path
                  charts {
                      edges {
                          cursor
                          node {id dir name path text yaml}
                      }
                  }
              }
          }
      }`, {id})

}

export function fetchYamlFile(path) {
  let id = toGlobalId("File", path);
  return fetchQuery(modernEnvironment, graphql`
      query FileViewsYamlFileQuery ($id: ID!) {
          node (id: $id) {
              id
              ... on File {id dir name path text yaml}
          }
      }`, {id})
}

function updateText(path, text) {
  // returns a relay.Disposable
  let id = toGlobalId("File", path);
  return commitMutation(modernEnvironment, {
    mutation: graphql`
        mutation FileViewsTextMutation($input: MutateTextFileInput!) {
            updateText (input: $input) {
                file { id name path text yaml}
            }
        }
    `,
    variables: {
      input: {id, text, clientMutationId: inc()},
    },
    configs: []
  });
}

//note: use the same resolver as the writer
function updateYaml(path, data) {
  let id = toGlobalId("File", path);
  return commitMutation(modernEnvironment, {
    mutation: graphql`
        mutation FileViewsYamlMutation($input: MutateYamlFileInput!) {
            updateYaml (input: $input) {
                file { id name path text yaml}
            }
        }
    `,
    variables: {
      input: {id, data, clientMutationId: inc()},
    },
    configs: []
  });
}

const StyledText = styled.pre`
  overflow: auto
`;

export function TextView({path, ansi = false}) {
  //todo: add scroll bar
  const [text, setText] = useState("");
  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    fetchTextFile(path).then(({node, errors}) => {
      if (running) {
        if (node) setText(node.text || "");
        else setText("");
      }
    });
    return abort;
  }, [path, setText]);
  return <StyledText>{ansi ? <Ansi>{text}</Ansi> : text}</StyledText>;
}

export function TextEditor({path, content = null, onChange = true, ..._props}) {
  //todo: add scroll bar
  if (onChange === true) onChange = (value) => updateText(path, value);
  else if (!onChange) onChange = undefined;

  const [text, setText] = useState("");
  useEffect(() => {
    if (content !== null) return setText(content);
    fetchTextFile(path).then(({node, errors}) => {
      if (node) setText(node.text || "");
      else setText("");
    });
  }, [path, content, setText, ...Object.values(_props)]);
  return <MonacoEditor width="100%"
                       height="100%"
                       language="yaml"
                       theme="vs-github"
                       value={text}
                       options={{
                         selectOnLineNumbers: true,
                         folding: true,
                         automaticLayout: true
                       }}
                       onChange={onChange}
                       editorDidMount={() => null}/>
}

export function ImageView({width = "100%", height = "100%", src}) {
  //todo: add scroll bar
  return <Image src={src} style={{
    maxWidth: width, maxHeight: height,
    objectFit: "contain",
    width: width, height: height,
    imageRendering: "pixelated",
    borderRadius: 10
  }}/>;
}

export function VideoView({width = "100%", height = "100%", src}) {
  //todo: add scroll bar
  if (!src) return <span>still loading</span>;
  return <Video style={{
    maxWidth: width, maxHeight: height,
    objectFit: "contain",
    borderRadius: 10
  }}>
    <source key="video" src={src} type="video/mp4"/>
    {/*<track key="cc" label="English" kind="subtitles" srcLang="en" src="/assets/small-en.vtt" default/>*/}
  </Video>
}

export const StyledTitle = styled(RowContainer)`
  height: 18px;
  margin: 3px 0;
  box-sizing: border-box;
  height: 1.5em;
  text-align: center;
  cursor: pointer;
  overflow: hidden;
  
  > .title {
    flex: 0 0 auto;
    display: inline-block;
    border-radius: 10px;
    color: #555;
    font-weight: 500;
    &:hover {
      color: white;
      background: #23aaff;
    }
    padding: 0 1em;
    height: 1.5em;
    line-height: 1.5em;
    position:relative;
    .close {
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
      margin: auto 3px;
    }
  }
  > .spacer {
    flex: 1 1 auto;
  }
  > .input {
    border: solid 1px #23aaff;
    margin: -1px;
    color: #23aaff;
    font-weight: 700;
    background: white;
  }
  > .control {
    flex: 0 0 auto;
    display: inline-block;
    color: black;
    opacity: 0.6;
    margin: 0 3px;
    border-radius: 10px;
    width: 1.5em;
    height: 1.5em;
    padding: 0 0.7em;
    &:hover {
      color: white;
      background: gray;
    }
    position: relative;
    svg {
      stroke-width: 3;
      width: 12px;
      height: 12px;
      stroke-width: 3;
      width: 12px;
      height: 12px;
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      margin: auto;
    }
  }
`;

const MainContainer = styled.div`
  height: 200px; 
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export default function InlineFile({type, prefix, glob, title, src, ...chart}) {
  const [files, setFiles] = useState([]);
  const [index, setIndex] = useState(-1);
  const [showConfig, toggleShowConfig] = useToggle();

  //does not allow multiple directories
  // if (typeof cwd === 'object') return null;

  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    globFiles({cwd: prefix, glob}).then(({glob, errors}) => {
      if (running && glob)
        setFiles([...glob].sort(by(strOrder, "path")));
    });
    return abort;
  }, [prefix, glob, setFiles]);

  const selected = files[index >= 0 ? index : (files.length + index)];
  const pathPrefix = commonPrefix(files.map(({path}) => path));

  src = src || (selected
      ? pathJoin(store.value.profile.url, "files", selected.path.slice(1))
      : null);

  // if type === "file" type = fileTypes(src);
  let viewer; // only render if src is valid. Otherwise breaks the video component.
  if (type === "video" && src) viewer = <VideoView src={encodeURI(src)}/>;
  else viewer = <MainContainer><ImageView src={encodeURI(src)}/></MainContainer>;

  return <>
    <Box>
      <StyledTitle onClick={() => toggleShowConfig(!showConfig)}>
        <span className="spacer"/>
        <span className="title" title={selected && selected.path}
              padding="2em">{selected ? selected.name : (title || "N/A")}</span>
        <span className="spacer"/>
      </StyledTitle>{viewer}
    </Box>
    {showConfig
        ? <div>
          <Box direction={"row"} gap={'none'} height={30}>
            <RangeInput value={index}
                        min={-10} max={files.length - 1}
                        style={{
                          margin: 0,
                          width: 100,
                          height: "30px",
                          display: "inline-block"
                        }}
                        onChange={e => setIndex(parseInt(e.target.value))}/>
            <input style={{
              width: 40, height: "30px", margin: 0, border: 0, boxSizing: "border-box",
              background: "transparent",
              marginLeft: "5px",
              textAlign: "center"
            }}
                   type="number"
                   value={index}
                   onChange={e => setIndex(parseInt(e.target.value))}/>
          </Box>
          {/*make multiple col span wide*/}
          {selected
              ? <>
                <p>
                  <strong>glob</strong>: <span style={{display: "inline-block"}}>{glob}</span>
                </p>
                <p>
                  <strong>file</strong>:
                  <span style={{display: "inline-block", wordBreak: "break-word"}}>{
                    subPrefix(selected.path, pathPrefix)}</span>
                </p>
              </>
              : null}
        </div>
        : null}
  </>
}

export function InlineChart({configPath = null, onRefresh = null, title, ...chart}) {
  //path is the link to the chart file
  const [showEditor, toggleEditor] = useToggle();

  if (!title) title = chart.yKey || chart.yKeys.join(', ');

  let numSpan = 1;
  if (chart.metricsGroups) numSpan = numOfFacets(chart);
  if (numOfLines(chart) > 3) numSpan *= 2;

  const style = {gridColumn: `span ${numSpan}`};

  const charts = (!!chart.metricsGroups) ? <CompoundChart {...chart}/> : <LineChart {...chart}/>

  return <>
    <Box style={style}>
      <StyledTitle>
        {!!onRefresh
            ? <span className="control" onClick={onRefresh}><RefreshCw color={"#afafaf"} height={12} width={12}/></span>
            : null}
        <span className="spacer"/>
        <span className="title" onClick={toggleEditor} title={title || "N/A"}>{title || "N/A"}</span>
        <span className="spacer"/>
      </StyledTitle>
      <MainContainer>{charts}</MainContainer>
    </Box>
    {(showEditor && configPath)
        ? <Box style={{gridColumn: "span 2"}}>
          <StyledTitle>
            <span className="spacer"/>
            <span className="title" title={configPath}>{configPath}</span>
            <span className="control" onClick={() => toggleEditor(false)}><X height={12} width={12}/></span>
            <span className="spacer"/>
          </StyledTitle>
          <MainContainer>
            <TextEditor path={configPath}/>
          </MainContainer>
        </Box>
        : null}
  </>
}

//id, dir, name, path, text, yaml: {}
export function AnyChart({type, ...chart}) {

  switch (type) {
    case "series":
      return <InlineChart key={JSON5.stringify(chart)} color="#23aaff" {...chart} />;
    case "file":
    case "video":
    case "mov":
    case "movie":
    case "img":
    case "image":
      // cwd={path} glob={chart.glob} src={chart.src}
      return <InlineFile type={type} {...chart}/>;
    default:
      return null;
  }
}