import React from 'react';
import graphql from 'babel-plugin-relay/macro';
import {toGlobalId} from "../../lib/relay-helpers";
import {
  Grid, Box, Accordion, AccordionPanel, Text, Table, TableHeader, TableCell, TableBody,
  TableRow,
  Tabs, Tab
} from "grommet";


export function DashPrepareVariables({username, project, path}) {
  return {
    id: toGlobalId("Directory", `/${username}/${project}/${path ? path : ""}`)
  }
}

export const DashQuery = graphql`
    query DashQuery($id: ID!) {
        directory (id: $id) {
            name
            directories (first:10) {
                edges {
                    node {
                        id name
                        directories (first:10) {
                            edges {
                                node {
                                    id name
                                }
                            }
                        }
                    }
                }
            }
            experiments (first:10) {
                edges { node {
                    id name
                    parameters {keys flat}
                } }
            }
        }
    }
`;

export default class Dash extends React.Component {
  render() {
    console.log(this.props);
    const {directory} = this.props;
    return <Grid fill={true} rows={['full']} columns={['medium', 'auto']} gap="small" areas={[
      {name: "nav", start: [0, 0], end: [0, 0]},
      {name: "main", start: [1, 0], end: [1, 0]},
    ]}>
      <Box gridArea="nav" background="darkgrey" fill={true}
           animation={["fadeIn", "slideRight"]}>
        navbar
      </Box>
      <Box gridArea="main" background="grey" fill={true} animation="fadeIn">
        main
      </Box>
    </Grid>;
  }
}
