import React from 'react';
import {Link} from 'found';

export default class ProjectSnippet extends React.Component {
  render() {
    console.log(this.props);
    const {username, name} = this.props;
    console.log(this.props);
    // const {username} = this.props.match.params;
    return (
        <Link to={ "/" + username + "/" + name + '/'}>
          <h1>ProjectSnippet</h1>
          <p>name: {name}</p>
        </Link>);
  }
}
