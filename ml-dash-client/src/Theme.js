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
    },
  },
  formField: {
    label: {
      margin: {left: '0px'},
      style: {
        fontWeight: 900,
        fontSize: "1em"
      }
    },
  },
  anchor: {
    color: "inherent",
    textDecoration: "none",
    hover: {
      textDecoration: "none",
    }
  }
};

function Theme(props) {
  return <Grommet theme={theme} {...props}/>
}

export default Theme;
