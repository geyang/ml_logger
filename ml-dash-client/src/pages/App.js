import React from 'react';
import graphql from 'babel-plugin-relay/macro';

export const query = graphql`
    query AppQuery ($username:String) {
        user (username: $username) {username name}
    }
`;

// $project:String,
// $path:String
// project (username: $username, project:$project) {id}
// path (username: $username, project:$project, path:$path) {id}

export default class App extends React.Component {
  render() {
    const props = this.props;
    const {username, project, path} = this.props.match.params;
    console.log({username, project, path});
    if (!props.user) return <div>user is null</div>;
    else return (<div>
      <p>
        ID: {props.user.username}, Name: {props.user.name}
      </p>
    </div>);
  }
}
