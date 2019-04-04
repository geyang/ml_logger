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

    const sortedDirectories = (directories && directories.edges || [])
        .map(({node}) => node)
        .filter(_ => _ !== null)
        .sort(by(strOrder, "name"))
        .reverse();

    const sortedExperiments = (experiments && experiments.edges || [])
        .map(({node}) => node)
        .filter(_ => _ !== null)
        .sort(by(strOrder, "name"))
        .reverse();

    return (
        <Box height={"100vh"}
            //rgba(229, 224, 250, 0.27)
             style={{boxShadow: "inset -20px 0 20px -8px rgba(245,245,250,0.9)"}}
             background="rgba(245,245,250,0.27)"
             gap='none'
             direction="column"
             {...props}>
          <Box align="center" justify="center">
            <h1>{directory.name}</h1>
          </Box>
          <Box gap='0.2em' direction="column" fill="vertical" flex={true}>
            <Box justify="center" pad='small' height="36px" flex={false}>
              <h4>Quick Selection</h4>
            </Box>
            <Box justify="center" pad='small' height="36px" flex={false}>
              <h4>Directories</h4>
            </Box>
            <Box gap='0.2em' direction="column" overflow={{vertical: "scroll"}} flex="shrink">
              {sortedDirectories.map((node) =>
                  <Button as={Link} to={node.path} key={node.path}>
                    <Box justify="center" pad='small'
                         key={node.id}
                         height="36px">
                      {node.name}
                    </Box></Button>)}
            </Box>
            <Box justify="center" pad='small' height="36px">
              <h4>Experiments</h4>
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
