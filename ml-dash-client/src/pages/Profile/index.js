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
    }`;

export default function Index({user}) {
  return (
      <Box fill={true} direction="row" justify='stretch' background="#fafafa">
        <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
          <Box animation="slideDown">
            {(user && user.username)
                ? <h1>Welcome, {user.username}!</h1>
                : <h1>Profile Page</h1>}
            <p>You have the following projects on the server.</p>
            <Box gap="small" overflow={"vertical"} style={{marginTop: "2em", marginBottom: "300px"}}>
              {user.projects.edges.map(({node}) =>
                  <ProjectSnippet key={node.id} username={user.username} name={node.name}/>
              )}
            </Box>
          </Box>
        </Box></Box>
  );
}
