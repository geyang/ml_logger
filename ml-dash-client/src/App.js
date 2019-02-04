import React from 'react';
import {QueryRenderer} from 'react-relay';
import graphql from 'babel-plugin-relay/macro';
import {modernEnvironment} from "./data";

export default class App extends React.Component {
  render() {
    return (
        <QueryRenderer
            environment={modernEnvironment}
            query={graphql`
              query AppQuery {
                empire { id name }
                rebels { id name }
                user {username name}
              }
            `}
            variables={{}}
            render={({error, props}) => {
              console.log(this.props);
              if (error) {
                return <div>Error!</div>;
              }
              if (!props) {
                return <div>Loading...</div>;
              }
              return <div>
                <p>
                ID: {props.empire.id}, Name: {props.empire.name}
                </p>
                <p>
                  ID: {props.user.username}, Name: {props.user.name}
                </p>
              </div>;
            }}
        />
    );
  }
}
