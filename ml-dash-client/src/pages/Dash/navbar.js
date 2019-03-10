import React from "react";
import {Box, Grid, Button} from "grommet/es6";
import {createFragmentContainer, createPaginationContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import Link from "found/lib/Link";
import {by, strOrder} from "../../lib/string-sort";

class Navbar extends React.Component {
  render() {
    const {directory, ...props} = this.props;
    console.log(directory, props);
    const {directories, experiments} = directory;

    const sortedDirectories = directories.edges
        .map(({node}) => node)
        .sort(by(strOrder, "name"))
        .reverse();

    const sortedExperiments = experiments.edges
        .map(({node}) => node)
        .sort(by(strOrder, "name"))
        .reverse();

    return (
        <Box height={"100vh"}
             gap='none'
             direction="column"
             {...props}>
          <Box align="center" justify="center">
            <h1>{directory.name}</h1>
          </Box>
          <Box gap='0.2em' direction="column" fill="vertical" flex={true}>
            <Box justify="center" pad='small' background='gray' height="36px" flex={false}>
              <h4 style={{color: "white"}}>Quick Selection</h4>
            </Box>
            <Box justify="center" pad='small' background='gray' height="36px" flex={false}>
              <h4 style={{color: "white"}}>Directories</h4>
            </Box>
            <Box gap='0.2em' direction="column" overflow={{vertical: "scroll"}} flex="shrink">
              {sortedDirectories.map((node) =>
                  <Button as={Link} to={node.path}>
                    <Box justify="center" pad='small'
                         key={node.id}
                         height="36px">
                      {node.name}
                    </Box></Button>)}
            </Box>
            <Box justify="center" pad='small' background='gray' height="36px">
              <h4 style={{color: "white"}}>Experiments</h4>
            </Box>
            <Box gap='0.2em' direction="column" overflow={{vertical: "scroll"}} flex="shrink">
              {sortedExperiments.map((node) =>
                  <Button as={Link} to={node.path}>
                    <Box justify="center" pad='small'
                         key={node.id}
                         height="36px">
                      {node.name}
                    </Box></Button>)}
            </Box>
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
