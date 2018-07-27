import React, {Component} from 'react';
import {fileApi} from '../lib/file-api';


export class Table extends Component {
    state = {};

    componentDidMount() {
        const {src, start, stop} = this.props;
        fileApi.getText(src, null, stop, start).then(content => this.setState({content}));
    }


    render() {
        const {content, render, start, stop, component: Component = 'pre'} = this.state;
        const _text = render ? render(content) : content;
        return <Component>{_text}</Component>
    }
}

