import React from 'react';
import {Box} from "grommet";
import Link from 'found/lib/Link';

export default class Index extends React.Component {
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
    return (
        <Box fill={true} direction="row" justify='stretch'>
          <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
            <Box animation="slideDown">
              <h1>ML-Dash</h1>
              <p>I have warned you.</p>
              <input type="text" onInput={this.onInput}/>
              <button onClick={this.login}>login</button>
              <br/>
              <br/>
              <Link to={"/" + this.state.username}>login:/{this.state.username}</Link>
            </Box></Box></Box>
    );
  }
}
