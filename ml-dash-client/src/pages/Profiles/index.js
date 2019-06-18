import React, {Fragment, useState, useEffect} from 'react';
import {Box, TextInput, Button, RadioButton, Anchor} from 'grommet';
import {Link} from "found";
import store from "../../local-storage";
import {Form, StyledForm, FormField, SubmitButton} from "../../components/Form";
import {equal} from "../../lib/object-equal";

export default function Profiles({match, router, ..._props}) {
  const [newProfile, setNewProfile] = useState({});
  const [{profile = {}, profiles = []}, setStoreValue] = useState(store.value);

  useEffect(() => store.subscribe(setStoreValue), []);

  return (<Box fill={true} direction="row" justify='stretch'>
    <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
      <Box animation="slideDown">
        <h1>Profiles</h1>
        <blockquote>These credentials are saved locally inside your browser.</blockquote>
        <Box gap='small'>
          {profiles.map(({username, url, accessToken}, index) =>
              <div>
                <div style={{left: "-3em", top: "3em", position: "relative"}}>
                  <RadioButton checked={equal({username, url, accessToken}, profile)}
                               onChange={() => store.selectProfile(index)}/>
                </div>
                <Box direction="row" style={{cursor: "pointer"}} onClick={() => router.push("/" + username)}>
                  <Box fill={true} style={{display: "block"}}>
                    <strong>Username</strong>: {username}
                    <br/>
                    <strong>API</strong>: {url}
                    <br/>
                    <strong>Access Token</strong>: {accessToken ? accessToken : "N/A"}
                  </Box>
                  <Button onClick={() => store.deleteProfile(index)}>
                    <Box>delete</Box>
                  </Button>
                </Box>
              </div>
          )}</Box>
        <h2 style={{marginTop: "4em", marginBottom: 0}}>Add New Profile</h2>
        <StyledForm style={{marginTop: 0, marginBottom: "300px"}}
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
