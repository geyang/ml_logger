import React, {} from "react";
import styled from "styled-components";

const Styled = styled.div`
  position: fixed;
  height: 42px;
  right: 0;
  top: 0;
  padding: 12px 20px;
  line-height: 24px;
  height: 48px;
  cursor: pointer;
  box-sizing: border-box;
  &:hover {
    background: rgba(0, 0, 0, 0.1);
  }`;

export default function ProfileBlock({profile}) {
  //place the redirect logic here
  return <Styled onClick={() => window.location.href = '/profiles'}>Hi, <strong>{profile.username}</strong>!</Styled>
}

export function ProfileSwitch() {
  return <Styled onClick={() => window.location.href = '/profiles'} style={{fontWeight: 500}}>Switch Profile</Styled>
}
