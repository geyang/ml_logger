import React, {useState, useEffect} from "react";
import styled from "styled-components";
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import {Box, Image, Video, RangeInput} from "grommet";

import {modernEnvironment} from "../data";
import {by, strOrder} from "../lib/string-sort";
import {pathJoin} from "../lib/path-join";
import store from "../local-storage";

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

export function ImageView({title, height, src}) {
  //todo: add scroll bar
  return <Image src={src} style={{
    maxWidth: 200, maxHeight: height,
    objectFit: "contain",
    borderRadius: 10
  }}/>;
}

export function VideoView({title, src}) {
  //todo: add scroll bar
  return <Video>
    <source key="video" src={src} type="video/mp4"/>
    {/*<track key="cc" label="English" kind="subtitles" srcLang="en" src="/assets/small-en.vtt" default/>*/}
  </Video>
}

const StyledTitle = styled.div`
  height: 18px;
  margin: 3px 0;
  text-align: center;
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
  height: 200px
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export default function InlineFile({type, cwd, glob, title, src, ...chart}) {
  const [files, setFiles] = useState([]);
  const [index, setIndex] = useState(-1);

  //does not allow multiple directories
  if (typeof cwd === 'object') return null;

  useEffect(() => {
    globFiles({cwd, glob}).then(data => {
      if (data && data.glob)
        setFiles([...data.glob].sort(by(strOrder, "name")));
    });
  }, [cwd, glob]);
  console.log(cwd);
  console.log(files);
  const selected = files[index >= 0 ? index : (files.length + index)];
  console.log(selected);
  console.log(index >= 0 ? index : (files.length + index));

  src = src ||
      (selected
          ? pathJoin(store.value.profile.url + "/files", selected.path.slice(1))
          : null);
  console.log(src);
  return <>
    <Box>
      <StyledTitle>
        <div className="title" title={selected && selected.path}>
          {selected ? selected.name : title}
        </div>
      </StyledTitle>
      <MainContainer>
        <ImageView src={encodeURI(src)} height={200}/>
      </MainContainer>
    </Box>
    <div>
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
    </div>
  </>
}

