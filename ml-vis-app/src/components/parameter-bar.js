import React, {Component} from 'react';
import {FlexItem} from "layout-components";
import styled from 'styled-components';
import {Link} from "react-router-dom";

export const ParamCell = styled.span`
    flex: 0 0 auto;
    margin: 0 0;
    display: flex;
    flex-direction: row;
    min-width: 60px;
    white-space: nowrap;
    &:not(:first-child) {
        margin-left: 20px;
    }
`;
export const ParamKey = styled.span`
    flex: 0 0 auto;
    padding: 0 4px 0 0;
`;
export const ParamValue = styled.span`
    flex: 0 0 auto;
    padding: 0 2px;
    font-weight: 900;
`;


export const ExpLink = styled(Link)`
    flex: 0 0 auto;
    color: #c6c6c6;
    font-weight: 300;
    text-decoration: none;
    &:hover {
        color: gray;
        text-decoration: underline;
    }
`;
