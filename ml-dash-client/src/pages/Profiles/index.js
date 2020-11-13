import React, {Fragment, useState, useEffect} from 'react';
import {Box, TextInput, Button, RadioButton, Anchor} from 'grommet';
import {Link} from "found";
import styled from "styled-components";
import store from "../../local-storage";
import {Form, StyledForm, FormField, SubmitButton} from "../../components/Form";
import {equal} from "../../lib/object-equal";

const StyledButton = styled.div`
  margin: 10px 0;
  padding: 10px;
  border-radius: 10px
  background: transparent;
  :hover {
    color: white;
    background: #ff2323;
  }
`;
const StyledBox = styled(Box)`
  margin-top: 10px;
  margin-left: -20px;
  margin-right: -20px;
  box-sizing: content-box;
  border-radius: 20px
  padding: 10px 20px;
  cursor: pointer;
  border: ${props => props.selected ? 'solid 2px #23aaff' : 'none'};
  :hover {
    color: white;
    background: #23aaff;
  }
`;

export default function Profiles({match, router, ..._props}) {
  const [newProfile, setNewProfile] = useState({});
  const [{profile = {}, profiles = []}, setStoreValue] = useState(store.value);

  useEffect(() => store.subscribe(setStoreValue), []);

  function selectProfile(index, username) {
    return () => {
      store.selectProfile(index)
      router.push("/" + username)
    }
  }

  function deleteProfile(index) {
    return (e) => {
      e.stopPropagation();
      store.deleteProfile(index)
    }
  }

  return (<Box fill={true} direction="row" justify='stretch'>
    <Box alignSelf={'center'} justifySelt={'center'} fill={true} direction="column" align="center"
         overflowY='auto'>
      <Box flex={false} animation="slideDown" style={{marginTop: "auto", marginBottom: "auto"}}>
        <h1 style={{marginTop: "4em"}}>Profiles</h1>
        <blockquote>These credentials are saved locally inside your browser.</blockquote>
        {profiles.map(({username, url, accessToken}, index) =>
            <StyledBox key={index}
                       direction="row"
                       selected={equal({username, url, accessToken}, profile)}
                       onClick={selectProfile(index, username)}>
              <Box fill={true} style={{display: "block"}}>
                <strong>Username</strong>: {username}
                <br/>
                <strong>API</strong>: {url}
                <br/>
                <strong>Access Token</strong>: {accessToken ? accessToken : "N/A"}
              </Box>
              <StyledButton onClick={deleteProfile(index)}>
                <Box>delete</Box>
              </StyledButton>
            </StyledBox>
        )}
        <h2 style={{marginTop: "4em", marginBottom: 0}}>Add New Profile</h2>
        <StyledForm style={{marginTop: 0, marginBottom: "8em"}}
                    onSubmit={(data) => store.addProfile(data)}>
          <FormField name="username" label="Username"/>
          <FormField name="url" label="API Url"/>
          <FormField name="accessToken" label="Access Token"/>
          <SubmitButton name="submit" primary>+ Add</SubmitButton>
        </StyledForm>
      </Box>
    </Box>
  </Box>);
}
