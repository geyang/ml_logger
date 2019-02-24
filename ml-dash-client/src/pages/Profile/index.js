import React from 'react';
import graphql from 'babel-plugin-relay/macro';
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
    return (<div>
      <h1>Profile Page</h1>
      <p>
        Name: {user.name}
        Username: {user.username}
        projects: {user.projects.edges.map(({node})=>
          <ProjectSnippet key={node.id} username={user.username} name={node.name}/>
      )}
      </p>
    </div>);
  }
}
