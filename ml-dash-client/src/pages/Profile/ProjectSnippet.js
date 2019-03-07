import React from 'react';
import {Link} from 'found';
import {Anchor, Button, Heading} from 'grommet';

export default function ProjectSnippet({username, name}) {
  // const {username} = this.props.match.params;
  return (
      <Button as={Link} to={"/" + username + "/" + name + '/'}
              style={{
                display: "block",
                background: "white",
                padding: "10px",
                borderRadius: "10px"
              }}
              padding='medium'>
        <Heading level={4} style={{margin: 0}}>{name}</Heading>
      </Button>
  );
}
