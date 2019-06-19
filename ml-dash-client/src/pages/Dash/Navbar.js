import React, {useState} from "react";
import {Box, Grid, Button} from "grommet/es6";
import {QueryRenderer, createFragmentContainer, createPaginationContainer, createRefetchContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import {by, strOrder} from "../../lib/string-sort";
import {Textfit} from "react-textfit";
import styled from "styled-components";
import {modernEnvironment} from "../../data";
import {toGlobalId} from "../../lib/relay-helpers";
import {Col, ColContainer, Row, RowContainer} from "../../components/layouts";

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
`;
const GrayButton = styled(StyledButton)`
  font-weight: 600;
  color: gray;
  :hover {
    box-shadow: 0 0 1px 0 #;
    color: black !important;
    background-color: #e6e6e6;
  }
`;

function Navbar({width, minWidth, height, fill, selected, print, directory, loadMore, onClickDir, ..._props}) {
  const {name, directories, experiments} = directory || {};

  const sortedDirectories = (directories && directories.edges || [])
      .filter(_ => _ !== null)
      .map(({node}) => node)
      .filter(_ => _ !== null)
      .sort(by(strOrder, "name"))
      .reverse();

  return (
      <ColContainer fill={fill}
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
            </StyledButton>)}
        <GrayButton onClick={loadMore}>Load More..</GrayButton>
      </ColContainer>);
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
