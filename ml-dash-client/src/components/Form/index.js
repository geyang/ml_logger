import React, {Fragment, createContext, useContext, useState} from "react";
import {Box, TextInput, Button} from "grommet";
import {useToggle} from "react-use";

import styled from "styled-components";

const FormContext = createContext();

export function FormField({name, label, value, ..._props}) {
  const {values, setValues} = useContext(FormContext);
  const [focus, toggleFocus] = useToggle(false);

  return <Fragment>
    <label className={(focus || values[name]) ? "focus" : null}>{label}</label>
    <TextInput type="text"
               value={values[name] || ""}
               onChange={(e) => setValues({...values, [name]: e.target.value})}
               onFocus={() => toggleFocus(true)}
               onBlur={() => toggleFocus(false)}/>
  </Fragment>
}

export function SubmitButton({name, children, ..._props}) {
  const {onSubmit} = useContext(FormContext);
  return <Button onClick={onSubmit} {..._props}>{children}</Button>;
}

export function Form({children, onSubmit, onChange, ..._props}) {
  const [values, setValues] = useState({});

  function _onChange() {
    if (typeof onChange === 'function')
      onChange(values)
  }

  function _onSubmit() {
    if (typeof onSubmit === 'function')
      onSubmit(values)
  }

  return <FormContext.Provider value={{values, setValues, onSubmit: _onSubmit}}>
    <form onChange={_onChange}
          onSubmit={_onSubmit}
          {..._props}>{children}</form>
  </FormContext.Provider>
}

export const StyledForm = styled(Form)`
  label {
    position: relative;
    transition: all 0.05s ease-out;
    line-height: 28px;
    top: 2.3em;
    font-size: 1.1em;
    margin-left: 1em;
    background: white
    z-index: 5;
  }
  label.focus, label.active {
    top: 0.8em;
    padding: 0 0.5em;
    font-size: 1em;
    margin-left: 0.4em;
    line-height: 28px;
  }
  button {
    height: 41px;
    padding: 0 1em;
    border-radius: 41px;
    margin-top: 21px;
    float: right;
  }
  
`;
