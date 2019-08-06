import React from 'react';
import graphql from 'babel-plugin-relay/macro';
import {Box} from "grommet";
import styled, {keyframes} from "styled-components";
import ProjectSnippet from "./ProjectSnippet";
import {ProfileSwitch} from "../../components/ProfileBlock";
import store from "../../local-storage";

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
  let {projects} = user;
  if (!projects || !projects.edges) projects = [];
  else projects = projects.edges;
  return (
      <Box fill={true} direction="row" justify='stretch' background="#fafafa">
        <ProfileSwitch/>
        <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
          <Box animation="slideDown" style={{maxWidth: "400px"}}>
            {(user && user.username)
                ? <h1>Welcome, {user.username}!</h1>
                : <h1>Profile Page</h1>}
            {projects.length
                ? <>
                  <p>You have the following projects on the server.</p>
                  <Box gap="small" overflow={"vertical"} style={{marginTop: "2em", marginBottom: "300px"}}>
                    {projects.map(({node}) => node)
                        .filter(_ => _ !== null)
                        .map(node =>
                            <ProjectSnippet key={node.id} username={user.username} name={node.name}/>
                        )}
                  </Box></>
                : <>
                  <p>Your logging folder is empty. To create your first run, try
                    running the following:.</p>
                  <pre>{`
from ml_logger import logger

logger.configure(log_directory="this-folder",
                 prefix='demo-project/first-run')
for i in range(100):
    logger.log(loss=0.9 ** i, step=i)
logger.log_text('charts: [{"yKey": "loss", "xKey": "step"}]', 
                ".charts.yml")
                  `}</pre>
                </>
            }
          </Box>
        </Box></Box>
  );
}

const fadeIn = keyframes`
    from { opacity: 0; }
    to   { opacity: 1; }
`;

const FadeIn = styled.span`
  opacity: 0;
  animation: ${fadeIn} 2s;
  animation-delay: 5s;
  animation-fill-mode: forwards;
`;

export function render({Component, props, error, match, ..._}) {
  const {profile} = store.value;
  if (!!error) {
    return <Box fill={true} direction="row" justify='stretch' background="#f0f0f0">
      <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
        <Box animation={["slideUp", "fadeIn"]}>
          <h2 style={{color: "red"}}>{error.toString()}</h2>
          <p>When loading the profile</p>
          <Box direction="row"
               style={{
                 cursor: "pointer",
                 display: "block",
                 background: "white",
                 padding: "10px",
                 borderRadius: "10px"
               }}
               onClick={() => match.router.push("/profiles")}>
            <Box fill={true} style={{display: "block"}}>
              <strong>Username</strong>: {profile.username}
              <br/>
              <strong>API</strong>: {profile.url}
              <br/>
              <strong>Access Token</strong>: {profile.accessToken ? profile.accessToken : "N/A"}
            </Box>
          </Box>
          <p>Click above to edit the configuration ☝️</p>
        </Box>
      </Box>
    </Box>;
  }
  if (!Component || !props)
    return <Box fill={true} direction="row" justify='stretch' background="#fafafa">
      <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
        <Box animation={["slideUp", "fadeIn"]}>
          <h1>Loading Your Profile</h1>
          <Box direction="row"
               style={{
                 cursor: "pointer",
                 display: "block",
                 background: "white",
                 padding: "10px",
                 borderRadius: "10px"
               }}
               onClick={() => match.router.push("/profiles")}>
            <Box fill={true} style={{display: "block"}}>
              <strong>Username</strong>: {profile.username}
              <br/>
              <strong>API</strong>: {profile.url}
              <br/>
              <strong>Access Token</strong>: {profile.accessToken ? profile.accessToken : "N/A"}
            </Box>
          </Box>
          <FadeIn>This is taking a bit long... click above to switch profiles</FadeIn>
        </Box>
      </Box>
    </Box>;
  return <Component {...props}/>;
}
