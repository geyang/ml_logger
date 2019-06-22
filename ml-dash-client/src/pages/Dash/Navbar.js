import React, {useEffect, useState} from "react";
import {Box, Grid, Button} from "grommet/es6";
import {QueryRenderer, createFragmentContainer, createPaginationContainer, createRefetchContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import {by, strOrder} from "../../lib/string-sort";
import {Textfit} from "react-textfit";
import styled from "styled-components";
import {modernEnvironment} from "../../data";
import {toGlobalId} from "../../lib/relay-helpers";
import {Col, ColContainer, Row, RowContainer} from "../../components/layouts";
import {AlertCircle, ArrowUpLeft, Delete, Edit3, FolderPlus, MoreVertical, Trash2, XCircle} from "react-feather";
import {useBoolean, useToggle} from "react-use";
import {deleteDirectory} from "./ExperimentDash";

const StyledButton = styled(Button)`
  flex: 0 0 auto;
  height: 24px;
  line-height: 24px
  padding: 0 10px;
  text-decoration: none;
  top: 0; botton: 0;
  ${props => props.selected ? "position: sticky;" : null}
  width: ${props => props.selected ? "100%" : "none"};
  color: ${props => props.selected ? "white" : "inherit!important"};
  background-color: ${props => props.selected ? "#23aaff" : "none"};
  border-radius: ${props => props.selected ? "12px 0 0 12px" : "12px"};
  :hover {
    box-shadow: 0 0 1px 0 #23aaff;
    background-color: #23aaff;
    color: white !important;
  }
  user-select: none;
  position: relative;
  .right-button {
    background: transparent;
    margin-left: 0.5em;
    display: inline-block;
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    vertical-align: middle;
    text-align: center;
    margin: auto 0;
    width: 24px;
    height: 24px;
    border-radius: ${props => props.selected ? "0" : "0 12px 12px 0"};
    opacity: 0.4;
    svg { stroke-width: 3; }
    :hover { 
      opacity: 1;
      box-shadow: 0 0 50px #4BA7E2;
    }
    :active:note(:active) {
      box-shadow: inset 0 0 5px #1E7CBB;
    }
  }
`;
const GrayButton = styled(StyledButton)`
  font-weight: 600;
  color: gray;
  :hover {
    box-shadow: 0 0 1px 0 #;
    color: black !important;
    background-color: #e6e6e6;
    font-size: 1em;
  }
`;
const ActionButton = styled(StyledButton)`
  padding-left: 1.8em;
  svg {
    position: absolute;
    width: 14px;
    height: 14px;
    margin: auto 0.5em auto 0;
    stroke-width 2;
    top: 0;
    bottom: 0;
    left: 0.45em;
  }
  ${props => props.color
    ? `
    color: ${props.color} !important;
    :hover {
      color: white;
      background: ${props.color};
    }
    ` : null}
`;
// const WarnButton = styled(ActionButton)`
//   color: red !important;
//   :hover {
//     color: white;
//     background: red;
//   }
// `;

const StyledContainer = styled(ColContainer)`
  .highlight + & {
    opacity: 0.2;
  }
  &.highlight {
    box-shadow: -40px 0 40px 0 #23aaff08;
  }
`;


function Navbar({
                  width, minWidth, height, fill, selected, print,
                  directory,
                  loadMore, onClickDir,
                  // onDeleteDirectory,
                  ..._props
                }) {
  const {name, path, directories, files, experiments} = directory || {};

  const sortedDirectories = (directories && directories.edges || [])
      .filter(_ => _ !== null)
      .map(({node}) => node)
      .filter(_ => _ !== null)
      .sort(by(strOrder, "name"))
      .reverse();

  const numOfDir = directory ? directories.edges.length : 0;
  const numOfFiles = files ? files.edges.length : 0;

  const [show, toggle] = useState(false);
  const [showConfirm, toggleShowConfirm] = useToggle(false);
  useEffect(() => {
    //note: does not work b/c the props are not updated.
    toggle(false);
  }, [name, path, numOfDir]);

  function onDelete() {
    toggle(false);
    toggleShowConfirm(false);
    deleteDirectory(show);
  }

  return <>
    <StyledContainer fill={fill}
                     style={{
                       width, height, minWidth,
                       boxShadow: "inset -20px 0 20px -8px rgba(245,245,250,0.9)",
                       background: "rgba(245,245,250,0.27)",
                     }} {..._props}>
      {sortedDirectories.map((node) =>
          <StyledButton
              key={node.path}
              onClick={() => onClickDir(node.path)}
              selected={selected === node.path}>
            {node.name}
            <div className="right-button" title="more directory options"
                 onClick={() => toggle(show ? false : node.path)}>
              <MoreVertical width="0.8em" height="0.8em"/>
            </div>
          </StyledButton>)}
      <GrayButton onClick={loadMore}>Load More..</GrayButton>
    </StyledContainer>
    {show ?
        <StyledContainer className="highlight">
          <ActionButton><FolderPlus width={10} height={10}/>New Folder</ActionButton>
          <ActionButton><Edit3 width={10} height={10}/>Rename</ActionButton>
          <ActionButton><ArrowUpLeft width={10} height={10}/>Move</ActionButton>
          <ActionButton color="#ff0000e0" onClick={() => toggleShowConfirm(true)}>
            <Trash2 width={10} height={10}/>Delete</ActionButton>
          {showConfirm ?
              <>
                <ActionButton onClick={() => toggleShowConfirm(false)}><XCircle width={10}
                                                                                height={10}/>Cancel</ActionButton>
                <ActionButton color="red" onClick={onDelete}><AlertCircle width={10} height={10}/>Confirm</ActionButton>
              </> : null}
          <ActionButton onClick={() => toggle(false)}><XCircle width={10} height={10}/>Close</ActionButton>
        </StyledContainer>
        : null}
  </>;
}

export default function ({path, ..._props}) {
  let dirID = toGlobalId("Directory", path);
  //todo: move all of these to the reFetch container inside the directory list view.
  //  so that we don't refresh the component on "loadMore"
  const [limit, setLimit] = useState(50);
  const [last, setLast] = useState();

  function loadMore() {
    setLimit(limit + 50)
  }

  return <QueryRenderer
      environment={modernEnvironment}
      cacheConfig={{force: true}}
      variables={{dirID, after: last, first: limit}}
      query={
        graphql`
        query NavbarQuery ($dirID:ID!, $first:Int, $after:String) {
            directory: node(id: $dirID){
                ...on Directory {
                    name
                    directories (first:$first, after:$after) {
                        pageInfo { endCursor hasNextPage }
                        edges { cursor node { id name path } }

                    }
                }
            }}
        `}
      render={
        ({error, props, retry}) => <Navbar loadMore={loadMore} {...props} {..._props}/>
      }/>;
}
