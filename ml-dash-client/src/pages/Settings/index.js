import React from 'react';
import {Box} from 'grommet';

export default function Settings(props) {
  const data = {
    user: {username: "episodeyang", name: "Ge Yang"},
    visServer: {
      api: ".../graphql",
      accessToken: "jwtToken"
    }
  };
  return (<Box fill={true} direction="row" justify='stretch'>
    <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
      <Box animation="slideDown">
        <h1>Settings</h1>
        <blockquote>These credentials are saved locally inside your browser.</blockquote>
        <h2>Account</h2>
        <p>
          <strong>Username</strong>: {data.user.username}<br/>
          <strong>Name</strong>: {data.user.name}
        </p>
        <h2>Servers</h2>
        <p>
          <strong>API</strong>: {data.visServer.api}<br/>
          <strong>Access Token</strong>: {data.visServer.accessToken}
        </p>
      </Box>
    </Box>
  </Box>);
}
