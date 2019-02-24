import React from 'react';
import {Grommet} from 'grommet';


const theme = {
  global: {
    animation: {
      duration: "0.2s"
    },
    font: {
      family: 'Roboto',
      size: '14px',
      height: '20px'
    }
  }
};

function Theme(props) {
  return <Grommet theme={theme} {...props}/>
}

export default Theme;
