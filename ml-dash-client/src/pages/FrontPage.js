import React from 'react';
import Link from 'found/lib/Link';

export default class FrontPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {username: null};
  }

  onInput = (e) => {
    this.setState({username: e.target.value});
  };

  login = (e) => {
    console.log(this.state.username);
  };

  render() {
    return (<div>
      <h1>ML-Dash</h1>
      <p>I have warned you.</p>
      <input type="text" onInput={this.onInput}/>
      <button onClick={this.login}>login</button>
      <br/>
      <br/>
      <Link to={"/" + this.state.username}>login:/{this.state.username}</Link>
    </div>);
  }
}
