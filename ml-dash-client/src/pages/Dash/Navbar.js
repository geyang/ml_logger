import React from "react";
import {Box, Grid, Button} from "grommet/es6";
import {createFragmentContainer, createPaginationContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import Link from "found/lib/Link";
import {by, strOrder} from "../../lib/string-sort";
import {Textfit} from "react-textfit";
import styled from "styled-components";
import {pathJoin, realPath} from "../../lib/path-join";

const StyledButton = styled(Button)`
  border-radius: 12px;
  height: 24px;
  line-height: 24px
  padding: 0 10px;
  text-decoration: none;
  color: inherit !important;
  :hover {
    box-shadow: 0 0 1px 0 #23aaff;
    background-color: #23aaff;
    color: white !important;
  }
  border-radius: 12px;
  height: 24px;
  line-height: 24px;
  padding: 0 10px;
  text-decoration: none;
  color: inherit !important;
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  overflow-y: auto;
  box-sizing: border-box;
  outline: none;
  max-width: 100%;
  flex: 0 1 auto;
  padding: 6px;
  flex-wrap: wrap;
`;

const StyledLink = styled(Link)`
  text-decoration: none;
  &:hover {
    color: inherit;
  }
  &:not(:hover) {
    color: #e6e6e6;
  }
`;

class Navbar extends React.Component {
  render() {
    const {directory, ...props} = this.props;
    console.log(directory, props);
    const {directories, experiments} = directory;

    const sortedDirectories = (directories && directories.edges || [])
        .filter(_ => _ !== null)
        .map(({node}) => node)
        .filter(_ => _ !== null)
        .sort(by(strOrder, "name"))
        .reverse();

    const sortedExperiments = (experiments && experiments.edges || [])
        .filter(_ => _ !== null)
        .map(({node}) => node)
        .filter(_ => _ !== null)
        .sort(by(strOrder, "name"))
        .reverse();

    return (
        <Box height={"100vh"}
             style={{boxShadow: "inset -20px 0 20px -8px rgba(245,245,250,0.9)"}}
             background="rgba(245,245,250,0.27)"
             gap='none'
             direction="column"
             {...props}>
          <Box align="center" justify="center" direction="column" height="80px">
            <Textfit forceSingleModeWidth={true}
                     style={{width: "90%", textAlign: "center", fontWeight: 600, marginRight: "2em"}}>
              <StyledLink to={realPath(pathJoin(window.location.pathname, "../"))}>../</StyledLink>
              {directory.name}
            </Textfit>
          </Box>
          <Box gap='0.2em' direction="column" fill="vertical" flex={true}>
            <Box justify="center" pad='small' height="36px" flex={false}>
              <h4>Quick Selection</h4>
            </Box>
            <Box justify="center" pad='small' height="36px" flex={false}>
              <h4>Directories</h4>
            </Box>
            <ButtonContainer>
              {sortedDirectories.map((node) =>
                  <StyledButton as={Link} to={node.path} key={node.path} style={{borderRadius: 10}}>
                    {node.name}
                  </StyledButton>)}
            </ButtonContainer>
            <Box justify="center" pad='small' height="36px">
              <h4>Experiments</h4>
            </Box>
            <ButtonContainer>
              {sortedExperiments.map((node) =>
                  <StyledButton as={Link} to={node.path}>
                    {node.name}
                  </StyledButton>)}
            </ButtonContainer>
          </Box>
        </Box>);
  }
}


export default createFragmentContainer(Navbar, {
  directory: graphql`
    fragment Navbar_directory on Directory {
      name
      directories (first:50) @connection(key: "Directory_directories"){
        edges {
          cursor
          node {
            id
            name
            path
            directories (first:5) {
              edges { node { id name } }
            }
          }
        }
      }
      experiments (first:10) @connection(key: "Directory_experiments"){
        edges { node {
          id name path
          parameters {keys flat}
        } }
      }

    }
  `
});
