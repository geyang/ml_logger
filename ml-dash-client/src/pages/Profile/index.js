import React from 'react';
import graphql from 'babel-plugin-relay/macro';
import {Box} from "grommet";
import ProjectSnippet from "./ProjectSnippet";

export const ProfileQuery = graphql`
    query ProfileQuery ($username:String) {
        user (username: $username) {
            username
            name
            projects (first:10) {
                edges {
                    node {id name}
                }
            }
        }
    }
`;

export default class Index extends React.Component {
  render() {
    const {user} = this.props;
    console.log(user);
    return (
        <Box fill={true} direction="row" justify='stretch' background="#eeeeee">
          <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
            <Box animation="slideDown">
              <h1>Profile Page</h1>
              <p>
                <strong>Username</strong>: {user.username}<br/>
                <strong>Name</strong>: {user.name}
              </p>
              <Box gap="small">
                <h1>projects:</h1>
                {user.projects.edges.map(({node}) =>
                    <ProjectSnippet key={node.id} username={user.username} name={node.name}/>
                )}
              </Box>
            </Box></Box></Box>);
  }
}
