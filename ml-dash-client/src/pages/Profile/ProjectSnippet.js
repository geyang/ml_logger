import React from 'react';
import {Link} from 'found';
import {Anchor, Button, Heading} from 'grommet';
import styled from "styled-components";

const StyledProjectSnippet = styled(Link)`
      display: block;
      background: white;
      padding: 10px;
      border-radius: 10px;
      &:hover {
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.04);
      }
      text-decoration: none;
      color: #444;
`;

export default function ProjectSnippet({username, name}) {
  return (
      <StyledProjectSnippet to={"/" + username + "/" + name + '/'} padding='medium'>
        <Heading level={4} style={{margin: 0}}>{name}</Heading>
      </StyledProjectSnippet>
  );
}
