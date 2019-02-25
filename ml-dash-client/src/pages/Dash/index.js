import React from 'react';
import graphql from 'babel-plugin-relay/macro';
import {toGlobalId} from "../../lib/relay-helpers";
import {Box, Grid} from "grommet";
import Navbar from "./Navbar";


export function DashPrepareVariables({username, project, path}) {
  return {
    id: toGlobalId("Directory", `/${username}/${project}/${path ? path : ""}`)
  }
}

export const DashQuery = graphql`
    query DashQuery($id: ID!) {
        directory (id: $id) {
            id
            name
            ... Navbar_directory
        }
    }
`;

export default class Dash extends React.Component {
  render() {
    console.log(this.props);
    const {directory} = this.props;
    return <Grid fill={true} rows={['full']} columns={['medium', 'auto']} gap="none"
                 areas={[
                   {name: "nav", start: [0, 0], end: [0, 0]},
                   {name: "main", start: [1, 0], end: [1, 0]},
                 ]}>
      <Navbar gridArea="nav" background="darkgrey" animation={["fadeIn", "slideRight"]}
              directory={directory}/>
      <Box gridArea="main" background="grey" fill={true} animation="fadeIn">
        main
      </Box>
    </Grid>;
  }
}
