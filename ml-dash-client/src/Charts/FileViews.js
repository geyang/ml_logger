import React, {useState, useEffect} from "react";
import {useToggle} from "react-use";
import styled from "styled-components";
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import {Box, Image, Video, RangeInput} from "grommet";
import Ansi from "ansi-to-react";

import {modernEnvironment} from "../data";
import {by, commonPrefix, strOrder, subPrefix} from "../lib/string-sort";
import {pathJoin} from "../lib/path-join";
import store from "../local-storage";
import LineChart from "./LineChart";

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

//todo: add chunked loading
const textFileQuery = graphql`
  query FileViewsTextFileQuery ($id: ID!) {
    file (id: $id) { text }
  }
`;

function fetchFile(id) {
  return fetchQuery(modernEnvironment, textFileQuery, {id})
}

const StyledText = styled.pre`
  overflow: auto
`;

export function TextView({id, ansi = false, width = "100%", height = "100%"}) {
  //todo: add scroll bar
  const [text, setText] = useState("");
  useEffect(() => {
    fetchFile(id).then(({file, errors}) => setText(file.text))
  }, [id]);
  return <StyledText>{ansi ? <Ansi>{text}</Ansi> : text}</StyledText>;
}

export function ImageView({width = "100%", height = "100%", src}) {
  //todo: add scroll bar
  return <Image src={src} style={{
    maxWidth: width, maxHeight: height,
    objectFit: "contain",
    borderRadius: 10
  }}/>;
}

export function VideoView({width = "100%", height = "100%", src}) {
  //todo: add scroll bar
  return <Video style={{
    maxWidth: width, maxHeight: height,
    objectFit: "contain",
    borderRadius: 10
  }}>
    <source key="video" src={src} type="video/mp4"/>
    {/*<track key="cc" label="English" kind="subtitles" srcLang="en" src="/assets/small-en.vtt" default/>*/}
  </Video>
}

export const StyledTitle = styled.div`
  height: 18px;
  margin: 3px 0;
  text-align: center;
  cursor: pointer;
  
  > .title {
    display: inline-block;
    border-radius: 10px;
    height: 18px;
    color: white;
    background: #23aaff;
    padding: 0 1em;
  }
`;

const MainContainer = styled.div`
  height: 200px; 
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export default function InlineFile({type, cwd, glob, title, src, ...chart}) {
  const [files, setFiles] = useState([]);
  const [index, setIndex] = useState(-1);
  const [showConfig, toggleShowConfig] = useToggle();

  //does not allow multiple directories
  if (typeof cwd === 'object') return null;

  useEffect(() => {
    globFiles({cwd, glob}).then(data => {
      if (data && data.glob)
        setFiles([...data.glob].sort(by(strOrder, "path")));
    });
  }, [cwd, glob]);
  const selected = files[index >= 0 ? index : (files.length + index)];
  const pathPrefix = commonPrefix(files.map(({path}) => path));

  src = src || (selected
      ? pathJoin(store.value.profile.url + "/files", selected.path.slice(1))
      : null);

  // if type === "file" type = fileTypes(src);
  let viewer; // only render if src is valid. Otherwise breaks the video component.
  if (type === "video" && src) viewer = <VideoView src={encodeURI(src)}/>;
  else viewer = <MainContainer><ImageView src={encodeURI(src)}/></MainContainer>;

  console.log(type, src, encodeURI(src));

  return <>
    <Box>
      <StyledTitle onClick={() => toggleShowConfig(!showConfig)}>
        <div className="title" title={selected && selected.path}>
          {selected ? selected.name : (title || "N/A")}
        </div>
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
          {selected
              ?
              <>
                <p direction={"row"} gap={'none'} height={30}>
                  <strong>glob</strong>: <span style={{display: "inlineBlock"}}>{glob}</span>
                </p>
                <p direction={"row"} gap={'none'} height={30}>
                  <strong>file</strong>:
                  <span style={{display: "inlineBlock"}}>{
                    subPrefix(selected.path, pathPrefix)}</span>
                </p>
              </>
              : null}
        </div>
        : null}
  </>
}

export function InlineChart({yKey, ...chart}) {
  return <Box>
    <StyledTitle onClick={() => null}>
      <div className="title" title={yKey}>{yKey}</div>
    </StyledTitle>
    <MainContainer>
      <LineChart yKey={yKey} {...chart}/>
    </MainContainer>
  </Box>
}
