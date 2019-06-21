import styled from "styled-components";
import React from "react";

const StyledEllipsis = styled.span`
  text-overflow: clip;
  position: relative;
  border-left: solid 0.5em transparent;
  padding-left: 0 !important;

  > span {
    min-width: 100%;
    position: relative;
    display: inline-block;
    float: right;
    overflow: visible;
  }
  `;


export default function Ellipsis({children, ..._}) {
  return <StyledEllipsis {..._}><span>{children}</span></StyledEllipsis>
}
