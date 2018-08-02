import React, {Component} from 'react';
import {FlexItem} from "layout-components";
import styled from 'styled-components';
import {Link} from "react-router-dom";

export const ParamCell = styled(FlexItem)`
    margin: 0 0;
    display: flex;
    flex-direction: row;
    min-width: 60px;
    &:not(:first-child) {
        margin-left: 20px;
    }
`;
export const ParamKey = styled(FlexItem)`
    padding: 0 4px 0 0;
`;
export const ParamValue = styled(FlexItem)`
    padding: 0 2px;
    font-weight: 900;
    font-style: bold;
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
