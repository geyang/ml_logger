import React from 'react';
import {Box} from "grommet";
import styled, {keyframes} from "styled-components";
import {useTimeout} from "react-use";
import store from "../../local-storage";

const fadeIn = keyframes`
    from { opacity: 0; }
    to   { opacity: 1; }
`;

const FadeIn = styled.span`
  animation: ${fadeIn} 2s;
`;

export default function Index() {
  const ready = useTimeout(2000);
  if (ready) {
    if (store.value.profile.username)
      window.location.href = `/${store.value.profile.username}`;
    else
      window.location.href = "/profiles";
  }

  return (
      <Box fill={true} direction="row" justify='stretch'>
        <Box alignSelf={'center'} justifySelt={'center'} fill="horizontal" direction="column" align="center">
          <Box animation={["slideUp", "fadeIn"]}>
            <h1>ML-Dash</h1>
            <h2 style={{marginBottom: 100}}>I have warned you. <FadeIn>😈</FadeIn></h2>
          </Box>
        </Box>
      </Box>
  );
}
