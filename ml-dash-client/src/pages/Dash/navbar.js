import React from "react";
import {Box, Grid} from "grommet/es6";
import {createFragmentContainer, createPaginationContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import Link from "found/lib/Link";

class Navbar extends React.Component {
  render() {
    const {directory, ...props} = this.props;
    console.log(directory, props);
    const {directories, experiments} = directory;
    return <Grid fill={true}
                 gap='none'
                 rows={['100px', 'auto']}
                 columns={['full']}
                 areas={[
                   {name: 'head', start: [0, 0], end: [0, 0]},
                   {name: 'main', start: [1, 0], end: [1, 0]},
                 ]} {...props}>
      <Box area="head" align="center" justify="center">
        <h1>{directory.name}</h1>
      </Box>
      <Box area="main" gap='none' overflow={{vertical: 'scroll'}}>
        <Box justify="center" pad='small' background='gray' height="36px">
          <h4 style={{color: "white"}}>Quick Selection</h4>
        </Box>
        <Box justify="center" pad='small' background='gray' height="36px">
          <h4 style={{color: "white"}}>Directories</h4>
        </Box>
        {directories.edges.map(({node}) =>
            <Box justify="center" pad='small'
                 key={node.id}
                 border={{side: "bottom", color: "gray", size: "1px"}} height="36px"
                 as={({className}) => <Link to={node.path} className={className}>{node.name}</Link>}/>)}
        <Box justify="center" pad='small' background='gray' height="36px">
          <h4 style={{color: "white"}}>Experiments</h4>
        </Box>
        {experiments.edges.map(({node}) =>
            <Box justify="center" pad='small'
                 key={node.id}
                 border={{side: "bottom", color: "gray", size: "1px"}} height="36px"
                 as={({className}) => <Link to={node.path} className={className}>{node.name}</Link>}/>)}
      </Box>
    </Grid>
  }
}


export default createFragmentContainer(Navbar, {
  directory: graphql`
      fragment Navbar_directory on Directory {
          name
          directories ( first:10 ) @connection(key: "Directory_directories"){
              edges {
                  cursor
                  node {
                      id
                      name
                      path
                      directories (first:10) {
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
