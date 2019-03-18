import React from "react";
import {commitMutation} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import {Box, Button} from "grommet";


export function ContextMenu({selected = [], deleteDirectory, ..._props}) {
  return <Box>
    <Button onClick={() => selected.forEach(deleteDirectory)}>
      {selected.length === 1
          ? `Delete Row`
          : `Delete ${selected.length} Rows`
      }</Button>
  </Box>
}
